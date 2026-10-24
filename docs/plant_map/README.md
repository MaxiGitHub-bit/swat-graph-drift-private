# SWaT engineering plant map (draft v0.1)

This folder holds the engineering map (graph) of the SWaT plant used by the
graph autoencoder. Every link is traced to a published design document.
The attack list was **not** used to draw any link.

## Files

| File | What it holds |
|---|---|
| `nodes.csv` | The 51 recorded devices: stage, sensor or actuator, Goh et al. (2017) Table 2 description, status (active, backup, not used, not implemented), notes on document errors |
| `link_register.csv` | One row per link: the two devices, link type, evidence level, source and note |
| `plant_map.png` | Drawing of the map (`python scripts/draw_plant_map.py`) |

## Link types

- **flow**: water passes from one device to the next (pipes in Fig. 2 or Table 2 descriptions)
- **control**: one reading switches or sets a device (stated in Table 2, or standard tank control)
- **shared_role**: a primary and its backup, or two parts of the same process step

## Evidence levels

- **documented**: stated in Goh et al. (2017), Fig. 2 or Table 2
- **inferred**: standard process engineering, not stated in the sources; must be checked before freezing
- **uncertain**: the source itself is contradictory; never used in any graph

Graph conditions built from this register (`src/swatlab/graph.py`):

| Condition | Links used |
|---|---|
| `engineering` | documented flow + control |
| `engineering_full` | documented + inferred flow + control |
| `random` | random links, same count as `engineering`, five seeds |
| `coarse` | same stage or same device type (as in Bello et al., 2026) |
| `none` | no links |

## Errors and conflicts found in the source documents

1. Table 2 lists LIT401 (a level transmitter) as an actuator.
2. Table 2 says AIT402 controls "NaHSO3 dosing (P203)"; P203 is the HCl pump and the NaHSO3 pump is P403.
3. Table 2 also says AIT402 controls NaOCl dosing (P205); kept as **uncertain** and unused.
4. Fig. 2 labels the dosing pumps P201 = HCl, P203 = NaOCl, P205 = NaCl; Table 2 says P201 = NaCl, P203 = HCl, P205 = NaOCl. The register follows Table 2 and marks the analyser-to-pump links as inferred.
5. Fig. 2 shows P301 and P401 as the duty pumps; Table 2 marks them as backups (P302 and P402 as duty).
6. Valve MV504 is mentioned elsewhere but is not one of the 51 recorded channels.

## Sources

Goh, J., Adepu, S., Junejo, K.N. and Mathur, A. (2017) 'A dataset to support research in the design of secure water treatment systems', in *Critical Information Infrastructures Security: CRITIS 2016*. LNCS 10242. Cham: Springer, pp. 88-99.

Mathur, A.P. and Tippenhauer, N.O. (2016) 'SWaT: a water treatment testbed for research and training on ICS security', in *2016 International Workshop on Cyber-physical Systems for Smart Water Networks (CySWater)*. IEEE, pp. 31-36.
