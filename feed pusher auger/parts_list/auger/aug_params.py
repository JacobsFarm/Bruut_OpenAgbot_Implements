# Wokkel (vijzel) van de feed pusher auger, los onderdeel volgens auger_specs.txt.
# Eigen assenstelsel: x = vijzelas, x 0 = kopse kant aandrijfkant, x = length = kopse kant passieve kant.
# y, z = dwars; hart as op y 0, z 0. Maten in mm.

# ---------------------------------------------------------------------
# Uit auger_specs.txt (gemeten)
# ---------------------------------------------------------------------
length = 1420.0                 # totale lengte van de wokkel (kernbuis)
core_d = 60.0                   # buitendiameter buis
core_id = 54.0                  # binnendiameter buis (aandrijfkant gemeten) -> wand 3
blade_d = 300.0                 # totale diameter met de vijzelbladen

shear_hole_x = 35.0             # aandrijfkant: hart breekboutgat vanaf de kopse kant
shear_hole_d = 12.4             # gat voor M12, dwars door de buis

bush_bore = 20.0                # slijtvaste kunststof ring in de buis (passieve kant): opening
bush_len = 30.0                 # dikte (lengte) van de ring
bush_od = core_id               # zit vast in de buis
# De vaste pen (Ø20 x 35) hoort bij de ophanging, niet bij de wokkel: niet getekend.

# ---------------------------------------------------------------------
# Geschat, niet gemeten
# ---------------------------------------------------------------------
blade_pitch = 260.0             # spoed (zelfde als V2), rechtsgangig: voert naar +x (passieve kant)
blade_t = 5.0                   # bladdikte
blade_x = (60.0, length - 10.0) # beblading: vrij van het breekboutgat, tot vlak bij de passieve kant
boss_d = 24.0                   # 2 opgelaste ringen boven en onder het breekboutgat: vlak vlak voor kop en borgmoer
boss_top = 35.0                 # vlakke bovenkant op 35 mm uit het hart (5 mm boven de buis)
shear_bolt_len = 90.0           # M12 x 90 breekbout: 2 x 35 + borgmoer 12 + 2 draad uitsteek (alleen ter illustratie)
lock_nut_h = 12.0               # M12 borgmoer (DIN 985)

rho_steel = 7.85e-6             # kg/mm3
rho_pe = 0.95e-6                # PE-UHMW
