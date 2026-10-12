"""The 20 image-defined risk factors (INRG staging system; Monclair et al., JCO 2009;
definitions per Brisse et al., Radiology 2011). Single source of truth for the API and UI."""

GROUPS = [
    {"id": "comp", "name": "Multiple compartments", "items": [
        {"id": "comp2", "t": "Ipsilateral extension across two body compartments (neck–chest, chest–abdomen or abdomen–pelvis)", "s": "Two compartments"}]},
    {"id": "neck", "name": "Neck", "items": [
        {"id": "neck_vessels", "t": "Encases the carotid or vertebral artery, or the internal jugular vein", "s": "Neck vessels"},
        {"id": "neck_skull", "t": "Extends to the base of the skull", "s": "Skull base"},
        {"id": "neck_trachea", "t": "Compresses the trachea", "s": "Trachea, neck"}]},
    {"id": "cerv", "name": "Cervico-thoracic junction", "items": [
        {"id": "ct_plexus", "t": "Encases the brachial plexus roots", "s": "Brachial plexus"},
        {"id": "ct_vessels", "t": "Encases the subclavian vessels, or the vertebral or carotid artery", "s": "Subclavian vessels"},
        {"id": "ct_trachea", "t": "Compresses the trachea", "s": "Trachea, junction"}]},
    {"id": "thor", "name": "Thorax", "items": [
        {"id": "th_aorta", "t": "Encases the aorta or its major branches", "s": "Thoracic aorta"},
        {"id": "th_airway", "t": "Compresses the trachea or main bronchi", "s": "Airway"},
        {"id": "th_costo", "t": "Lower mediastinal tumour infiltrating the costo-vertebral junction between T9 and T12", "s": "Costo-vertebral junction"}]},
    {"id": "thab", "name": "Thoraco-abdominal", "items": [
        {"id": "ta_vessels", "t": "Encases the aorta or vena cava", "s": "Aorta or IVC, thoraco-abdominal"}]},
    {"id": "abd", "name": "Abdomen and pelvis", "items": [
        {"id": "ab_porta", "t": "Infiltrates the porta hepatis or hepatoduodenal ligament", "s": "Porta hepatis"},
        {"id": "ab_smab", "t": "Encases branches of the SMA at the mesenteric root", "s": "SMA branches"},
        {"id": "ab_origin", "t": "Encases the origin of the coeliac axis or the SMA", "s": "Coeliac or SMA origin"},
        {"id": "ab_renal", "t": "Invades one or both renal pedicles", "s": "Renal pedicle"},
        {"id": "ab_aorta", "t": "Encases the aorta or vena cava", "s": "Aorta or IVC"},
        {"id": "ab_iliac", "t": "Encases the iliac vessels", "s": "Iliac vessels"},
        {"id": "ab_sciatic", "t": "Pelvic tumour crossing the sciatic notch", "s": "Sciatic notch"}]},
    {"id": "spine", "name": "Spinal canal", "items": [
        {"id": "spine", "t": "Intraspinal extension filling more than one third of the canal on axial images, or perimedullary spaces not visible, or abnormal cord signal", "s": "Intraspinal extension"}]},
    {"id": "organs", "name": "Adjacent organs", "items": [
        {"id": "organs", "t": "Infiltrates the pericardium, diaphragm, kidney, liver, duodeno-pancreatic block or mesentery", "s": "Adjacent organs"}]},
]

ITEMS = [dict(it, g=g["id"]) for g in GROUPS for it in g["items"]]
ITEM_IDS = [i["id"] for i in ITEMS]
SHORT = {i["id"]: i["s"] for i in ITEMS}
VALID = {"absent", "present", "na"}

assert len(ITEM_IDS) == 20 and len(set(ITEM_IDS)) == 20
