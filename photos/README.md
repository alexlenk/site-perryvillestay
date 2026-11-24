# Photos – originals, edits and the Airbnb upload set

As of 2026-11-24. Background and decisions: family knowledge base, `Properties/Perryville/Perryville-House.md` ("Photos" and "Airbnb photo update").

## Folders

- `originals/` – the unedited source photos the edits start from (owners' own photos, re-saved without metadata). `house-airbnb-cover.jpg` is the current Airbnb cover photo as downloaded from the public listing (2560 px). The owners' private bedroom photos (IMG_9487/9488) are deliberately not stored.
- `airbnb-upload/` – ~~the 9 edited photos~~ 16 edited photos at full size (since 2026-11-24, later the same day), numbered in the suggested Airbnb order (01 = cover). 01, 02, 04, 05, 07, 10, 11, 13, 14 are the same edits as `../images/` (the 1440/800 px website versions); 03, 06, 08, 09, 12, 15, 16 are only here. The house number (335) is removed in every photo that showed it (01, 15, 16 and the website/print house photo).
- `edit/` – the Python scripts used on 2026-11-24. They were run in a Claude cloud session and contain that session's absolute paths (`/tmp/claude-0/...`, upload ids); adjust the paths before reuse. Mapping of upload ids to files: `8de75834` kitchen, `11b621e1` bedroom-desk, `2512033c` living-and-kitchen, `f6ddc7c8` living-room, `8d82d17c` bedroom, `6d28b7f6` dining, `5e4cd524` bathroom, `7cf0a005` shower, `9ebf4ab7` spring house photo, `3edd4fda` desk close-up, `0c58f675` dining to living, `26ff065e` kitchen and dining, `4a2d6af5` hallway, `3d76fe60` living room towards the entry, `bb4c4e07` front door, `01583849` house and driveway, `/tmp/claude-0/airbnb/big_2560.jpg` Airbnb cover.

## Pipeline

1. **Remove items** – `lama.py` (LaMa inpainting per masked blob), `lama_lowres.py` (whole image at half resolution for large areas such as the TV stand). Masks are hand-traced polygons in `process_all.py`, `clean_bed3.py` (desk cables, printer, tag) and `house_old.py` (bin, AC unit, power line). `fix_hole.py` rebuilds the house wall behind the removed bin by cloning siding from right of the porch post.
2. **Straighten** – `upright.py` (`rotH`, `inner_crop`), auto-fitted in `process_all.py`; at most the share of the tilt that keeps 85 % of the width; the shower is not straightened.
3. **Light and colour** – interiors: `colour.py` (cream walls b* ≈ 7, white ceiling b* ≈ 1.5 via traced ceiling outlines) on top of `light2.py`; house: `house_colour_wall.py` (brightening that keeps saturation; sun glare kept on purpose); `house_colour_final.py` is the same on the version without the house number.
4. **Added photos (second batch)** – `new_photos.py`: house number removed (cover, front door, house with driveway), items removed (desk cables, coasters and envelope, table items, kitchen counter clutter and the device and outlet plug right of the stove, box on the TV stand), straightened and coloured like the rest; interiors use `colour.py`, exteriors the saturation-keeping brightening. `gridcrop.py` draws the coordinate grids used to trace the masks.

## LaMa model

`big-lama.pt` from the GitHub release of enesmsahin/simple-lama-inpainting v0.1.0 (205,803,670 bytes, sha256 `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`), run with PyTorch on CPU (`torch.jit.load`). Not stored here because of its size. In a Claude cloud session, running the model needed the "Accept edits" permission mode (auto mode blocked it as running downloaded code).
