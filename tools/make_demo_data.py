"""Create synthetic neuroblastoma CT phantoms as real DICOM series, for testing the installation.

    python tools/make_demo_data.py            # writes into ./data (or DATA_DIR from .env)
    python tools/make_demo_data.py D:/some/folder

Writes data/dicom/DEMO_P1_dx ... DEMO_P4_post and data/cases.csv. The images are drawn by code:
no patient data is involved. Patient 1's diagnosis folder also holds a non-contrast series, to check
that the importer picks the contrast-enhanced one.
"""
import csv
import sys
from pathlib import Path

import numpy as np
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

N, Z, H = 256, 90, 128.0
PIX, THK = 1.1, 2.5
yy, xx = np.mgrid[0:N, 0:N]
X = (xx + 0.5 - H) / H
Y = (yy + 0.5 - H) / H


def val(v, zn):
    return v(zn) if callable(v) else v


def E(cx, cy, rx, ry, hu, zc=0.5, zh=0.6, flat=True, tex=0, fn=None):
    return ("e", cx, cy, rx, ry, hu, zc, zh, flat, tex, fn)


def S(pts, r, z0, z1, hu):
    return ("s", pts, r, z0, z1, hu)


def tex(z):
    return np.sin(xx * 0.31 * 256 / N + z * 0.17) * np.cos(yy * 0.27 * 256 / N - z * 0.11)


def paint(sl, s, zn, z):
    if s[0] == "e":
        _, cx, cy, rx, ry, hu, zc, zh, flat, tx, fn = s
        d = (zn - zc) / zh
        if d < -1 or d > 1:
            return
        sc = 1.0 if flat else np.sqrt(1 - d * d)
        cx, cy, rx, ry = val(cx, zn), val(cy, zn), val(rx, zn) * sc, val(ry, zn) * sc
        if rx <= 0.002 or ry <= 0.002:
            return
        m = ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1
        if fn is not None:
            v = fn(z)
            if v is None:
                return
            sl[m] = v[m] if isinstance(v, np.ndarray) else v
        else:
            sl[m] = (hu + tx * tex(z))[m] if tx else hu
    else:
        _, pts, r, z0, z1, hu = s
        if zn < z0 or zn > z1:
            return
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            vx, vy = bx - ax, by - ay
            t = np.clip(((X - ax) * vx + (Y - ay) * vy) / (vx * vx + vy * vy), 0, 1)
            m = (X - (ax + t * vx)) ** 2 + (Y - (ay + t * vy)) ** 2 <= r * r
            sl[m] = hu


def anatomy(rng):
    A = [E(0, 0.05, 0.84, 0.64, -95), E(0, 0.05, 0.80, 0.60, 48, tex=4), E(0, 0.055, 0.755, 0.55, -75, tex=6),
         E(-0.42, 0.28, 0.30, 0.28, -840, 0, 0.15, False, 25), E(0.44, 0.28, 0.28, 0.28, -840, 0, 0.13, False, 25),
         E(-0.33, -0.02, 0.42, 0.45, 104, 0.2, 0.32, False, 5), E(-0.20, 0.02, 0.05, 0.035, 185, 0.27, 0.06, False),
         E(-0.32, -0.24, 0.07, 0.09, 8, 0.36, 0.07, False), E(0.53, 0.12, 0.19, 0.25, 118, 0.18, 0.2, False, 4),
         E(0.30, -0.22, 0.24, 0.16, 55, 0.12, 0.14, False),
         E(0.30, -0.22, 0.20, 0.125, 0, 0.12, 0.13, False, fn=lambda z: np.where(Y < -0.25, -880, 18)),
         E(0.10, -0.03, 0.30, 0.06, 88, 0.30, 0.07, False, 5)]
    for kx, kz in ((0.42, 0.48), (-0.40, 0.52)):
        sg = np.sign(kx)
        A += [E(kx, 0.26, 0.13, 0.17, 165, kz, 0.2, False, 5), E(kx - sg * 0.06, 0.25, 0.05, 0.07, -45, kz, 0.1, False)]
    A += [E(-0.56, 0.0, 0.075, 0.075, 58, 0.66, 0.34), E(-0.56, 0.0, 0.05, 0.05, -860, 0.66, 0.34, True, 30),
          E(0.60, 0.06, 0.06, 0.06, 58, 0.6, 0.4), E(0.60, 0.06, 0.038, 0.038, -860, 0.6, 0.4, True, 30)]
    for _ in range(14):
        cx, cy, zc, zh = -0.45 + rng.random() * 0.95, -0.44 + rng.random() * 0.44, 0.45 + rng.random() * 0.5, 0.05 + rng.random() * 0.06
        r, air = 0.04 + rng.random() * 0.035, rng.random() < 0.45
        A += [E(cx, cy, r, r, 62, zc, zh, False), E(cx, cy, r * 0.62, r * 0.62, -860 if air else 22, zc, zh * 0.9, False, 30 if air else 4)]
    for s in (-1, 1):
        A += [E(s * 0.56, 0.22, 0.06, 0.2, 560, 0.95, 0.2, False, 60),
              E(s * 0.17, 0.30, lambda zn: 0.03 + 0.08 * zn, lambda zn: 0.035 + 0.08 * zn, 50, 0.7, 0.35, True, 3),
              E(s * 0.13, 0.55, 0.085, 0.065, 52, tex=3)]
    return A


def spine():
    gap = lambda n, hu: (lambda z: None if z % 12 < n else hu)
    return [E(0, 0.565, 0.085, 0.03, 0, fn=gap(3, 620)), E(0, 0.615, 0.02, 0.045, 0, fn=gap(4, 620)),
            E(-0.07, 0.455, 0.025, 0.055, 0, fn=gap(3, 620)), E(0.07, 0.455, 0.025, 0.055, 0, fn=gap(3, 620)),
            E(0, 0.33, 0.10, 0.085, 0, fn=lambda z: 92 if z % 12 < 2 else 720),
            E(0, 0.33, 0.078, 0.066, 0, fn=lambda z: 92 if z % 12 < 2 else 245 + 30 * tex(z)),
            E(0, 0.48, 0.045, 0.048, 12), E(0, 0.475, 0.022, 0.026, 34, 0.3, 0.35)]


VESSELS = [
    E(0.05, 0.18, 0.052, 0.052, 240, 0.4, 0.4),
    E(lambda zn: 0.05 + (zn - 0.8) * 1.5, lambda zn: 0.18 + (zn - 0.8) * 0.35, 0.034, 0.034, 240, 0.9, 0.1),
    E(lambda zn: 0.05 - (zn - 0.8) * 1.5, lambda zn: 0.18 + (zn - 0.8) * 0.35, 0.034, 0.034, 240, 0.9, 0.1),
    E(-0.12, 0.19, 0.06, 0.045, 190, 0.43, 0.39),
    E(lambda zn: -0.01 + (zn - 0.82) * 1.35, lambda zn: 0.23 + (zn - 0.82) * 0.3, 0.036, 0.03, 190, 0.91, 0.09),
    E(lambda zn: -0.05 - (zn - 0.82) * 1.35, lambda zn: 0.23 + (zn - 0.82) * 0.3, 0.036, 0.03, 190, 0.91, 0.09),
    S([(0.05, 0.14), (0.05, 0.02)], 0.018, 0.18, 0.23, 240), S([(0.05, 0.02), (-0.20, 0.0)], 0.014, 0.205, 0.23, 240),
    S([(0.05, 0.02), (0.36, 0.06)], 0.015, 0.20, 0.225, 240), S([(0.05, 0.18), (0.05, 0.12)], 0.019, 0.25, 0.285, 240),
    E(lambda zn: 0.05 - (zn - 0.25) * 0.1, lambda zn: 0.12 - min(zn - 0.25, 0.1), 0.02, 0.02, 240, 0.55, 0.3),
    E(lambda zn: -0.01 - (zn - 0.25) * 0.1, lambda zn: 0.125 - min(zn - 0.25, 0.1), 0.026, 0.026, 190, 0.575, 0.275),
    S([(0.08, 0.19), (0.34, 0.25)], 0.014, 0.42, 0.45, 240), S([(0.02, 0.2), (-0.13, 0.255), (-0.32, 0.26)], 0.014, 0.43, 0.46, 240),
    S([(0.35, 0.23), (0.10, 0.105), (-0.10, 0.17)], 0.02, 0.45, 0.49, 190), S([(-0.31, 0.245), (-0.14, 0.21)], 0.021, 0.47, 0.51, 190),
]

PATIENTS = [
    dict(id="P1", seed=101, calc=28, necrosis=True,
         base=[(0.20, 0.10, 0.40, 0.22, 0.18, 0.16), (0.08, 0.12, 0.35, 0.16, 0.14, 0.12), (0.10, 0.08, 0.25, 0.12, 0.10, 0.08)],
         post=[(0.27, 0.16, 0.44, 0.12, 0.10, 0.09), (0.18, 0.14, 0.42, 0.07, 0.07, 0.06)]),
    dict(id="P2", seed=202, calc=20,
         base=[(-0.22, 0.14, 0.47, 0.20, 0.16, 0.15), (-0.10, 0.18, 0.50, 0.12, 0.10, 0.12)],
         post=[(-0.30, 0.10, 0.52, 0.07, 0.06, 0.05)]),
    dict(id="P3", seed=303, calc=32, necrosis=True,
         base=[(0.04, 0.10, 0.28, 0.20, 0.16, 0.14), (0.00, 0.20, 0.35, 0.14, 0.12, 0.12), (-0.08, 0.05, 0.32, 0.12, 0.10, 0.08), (0.13, 0.33, 0.33, 0.06, 0.08, 0.07)],
         post=[(0.04, 0.12, 0.30, 0.10, 0.09, 0.08), (0.13, 0.35, 0.33, 0.03, 0.04, 0.04)],
         sp_base=[(0.025, 0.47, 0.33, 0.04, 0.04, 0.05), (0.08, 0.42, 0.33, 0.045, 0.035, 0.05)],
         sp_post=[(0.035, 0.465, 0.33, 0.018, 0.018, 0.03), (0.09, 0.415, 0.33, 0.03, 0.025, 0.03)]),
    dict(id="P4", seed=404, calc=10,
         base=[(0.36, 0.10, 0.36, 0.10, 0.09, 0.08)], post=[(0.37, 0.10, 0.36, 0.06, 0.055, 0.05)]),
]


def blobs(sl, bl, zn, z, base, ph, lob=0.08):
    for bi, (cx, cy, cz, rx, ry, rz) in enumerate(bl):
        d = (zn - cz) / rz
        if d <= -1 or d >= 1:
            continue
        sc = np.sqrt(1 - d * d)
        dx, dy = (X - cx) / (rx * sc), (Y - cy) / (ry * sc)
        lim = 1 + lob * np.sin(3 * np.arctan2(dy, dx) + ph + bi * 1.7 + z * 0.05)
        m = dx * dx + dy * dy <= lim * lim
        sl[m] = (base + 9 * np.sin(xx * 0.35 + ph) * np.cos(yy * 0.29 - z * 0.2) + 6 * np.sin(z * 0.41 + xx * 0.13))[m]


def volume(p, post):
    rng = np.random.default_rng(p["seed"] * 7 + (3 if post else 1))
    A, SP = anatomy(rng), spine()
    bl = p["post"] if post else p["base"]
    sp = p.get("sp_post" if post else "sp_base")
    b0 = bl[0]
    nec = [(b0[0], b0[1], b0[2], b0[3] * 0.42, b0[4] * 0.42, b0[5] * 0.42)] if p.get("necrosis") and not post else None
    crng = np.random.default_rng(p["seed"] * 13 + (5 if post else 2))
    calcs = []
    for _ in range(int(round(p["calc"] * (0.8 if post else 1)))):
        b = bl[crng.integers(len(bl))]
        while True:
            u = crng.uniform(-1, 1, 3)
            if (u ** 2).sum() <= 0.6:
                break
        calcs.append(((b[0] + u[0] * b[3]) * H + H - 0.5, (b[1] + u[1] * b[4]) * H + H - 0.5, (b[2] + u[2] * b[5]) * (Z - 1),
                      (0.9 + crng.random() * 1.3) * N / 192, 380 + crng.random() * 420))
    nrng = np.random.default_rng(p["seed"] * 17 + (9 if post else 4))
    vol = np.empty((Z, N, N), np.int16)
    base, ph = (30 if post else 38), p["seed"] % 7
    for z in range(Z):
        zn = z / (Z - 1)
        sl = np.full((N, N), -1000.0)
        for s in A:
            paint(sl, s, zn, z)
        blobs(sl, bl, zn, z, base, ph)
        if nec:
            blobs(sl, nec, zn, z, 16, ph, 0.03)
        for cx, cy, cz, rr, hu in calcs:
            dz = abs(z - cz)
            if dz <= 1.3:
                r = rr * (1 - dz / 1.6)
                if r > 0.3:
                    sl[(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r] = hu
        for s in SP:
            paint(sl, s, zn, z)
        if sp:
            blobs(sl, sp, zn, z, base, ph, 0.02)
        for s in VESSELS:
            paint(sl, s, zn, z)
        sl = (np.roll(sl, 1, 1) + 2 * sl + np.roll(sl, -1, 1)) / 4
        sl = (np.roll(sl, 1, 0) + 2 * sl + np.roll(sl, -1, 0)) / 4
        sl += nrng.normal(0, 13, sl.shape)
        vol[z] = np.clip(sl, -1024, 3071).astype(np.int16)
    return vol


def write_series(vol, out, patient, desc, study_uid, series_no, thick=THK, contrast=True):
    out.mkdir(parents=True, exist_ok=True)
    series_uid = generate_uid()
    nz = vol.shape[0]
    for k in range(nz):
        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = CTImageStorage
        sop = generate_uid()
        meta.MediaStorageSOPInstanceUID = sop
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = Dataset()
        ds.file_meta = meta
        ds.SOPClassUID, ds.SOPInstanceUID = CTImageStorage, sop
        ds.Modality, ds.PatientName, ds.PatientID = "CT", "DEMO^PHANTOM", f"DEMO-{patient}"
        ds.StudyInstanceUID, ds.SeriesInstanceUID = study_uid, series_uid
        ds.SeriesDescription, ds.SeriesNumber, ds.InstanceNumber = desc, series_no, k + 1
        if contrast:
            ds.ContrastBolusAgent = "IV contrast"
        ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
        ds.ImagePositionPatient = [-N * PIX / 2, -N * PIX / 2, (nz - 1 - k) * thick]
        ds.PixelSpacing, ds.SliceThickness = [PIX, PIX], thick
        ds.Rows, ds.Columns, ds.SamplesPerPixel = N, N, 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated, ds.BitsStored, ds.HighBit, ds.PixelRepresentation = 16, 16, 15, 0
        ds.RescaleIntercept, ds.RescaleSlope = -1024, 1
        ds.PixelData = (vol[k].astype(np.int32) + 1024).clip(0, 65535).astype("<u2").tobytes()
        ds.save_as(out / f"IM{k + 1:04d}.dcm", enforce_file_format=True)


def main(data_dir):
    data = Path(data_dir)
    rows = []
    for i, p in enumerate(PATIENTS):
        for post in (False, True):
            name = f'DEMO_{p["id"]}_{"post" if post else "dx"}'
            vol = volume(p, post)
            study = generate_uid()
            write_series(vol, data / "dicom" / name / "venous", p["id"], "Abdomen PV 2.5mm", study, 3)
            if i == 0 and not post:  # decoy: thick non-contrast series in the same study
                write_series(vol[::2] - 60, data / "dicom" / name / "noncon", p["id"], "Abdomen non con 5mm", study, 2, thick=THK * 2, contrast=False)
            rows.append({"folder": name, "patient": p["id"], "timepoint": "post_induction" if post else "diagnosis",
                         "double_read": "yes" if i < 2 else "", "series": ""})
            print("wrote", name)
    with open(data / "cases.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["folder", "patient", "timepoint", "double_read", "series"])
        w.writeheader()
        w.writerows(rows)
    print("wrote", data / "cases.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else config.data_dir())
