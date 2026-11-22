# 3D-printed pin-on card pocket

Two versions of the same pocket:
- **One piece, printed standing up** (`card-pocket-upright.*`): simplest, no glue. Text in the same color.
- **Two parts, printed flat** (`card-pocket.*`, details further down): needs gluing, but the text can be a second color with few filament changes.

## One piece, printed standing up

Source: `card-pocket-upright.scad`. Size: 96.7 mm wide, 72 mm high, 14.4 mm deep including the raised text. Card slot 91.9 × 9 mm.

| File | What |
|---|---|
| `card-pocket-upright-pocket.stl` | The pocket with raised text, single color (print this one) |
| `card-pocket-upright-body.stl` + `card-pocket-upright-text.stl` | Same pocket split into body and text, only if you want the text in a second color |

Print as exported: pocket bottom on the bed, back plate and front wall standing. No supports. The base is only 13.8 mm deep and the back plate is 72 mm tall, so use a brim to keep it from tipping or warping. Two-color text on this vertical face means a filament change on every layer the text spans (about 75 layers at 0.2 mm), so single color is the practical choice.

## Two parts, printed flat

A pocket for about 20 US business cards (3.5 × 2 in) that hangs next to a flyer on a bulletin board with two push pins. Source: `card-pocket.scad` (OpenSCAD; all sizes are parameters at the top of the file).

Overall size: 99.9 × 72 mm, 15.8 mm deep with the front plate. The card slot is 91.9 mm wide and 9 mm deep.

## Files

| File | What | Print orientation |
|---|---|---|
| `card-pocket-back.stl` | Back plate with pin holes, U-shaped walls, alignment pegs | As exported: back plate flat on the bed, walls pointing up |
| `card-pocket-front.stl` | Front plate with thumb notch; blind peg holes underneath | As exported: face up |
| `card-pocket-text.stl` | Raised text, 0.6 mm, sits exactly on top of the front plate | Load together with the front plate (second color) |
| `card-pocket-front_single.stl` | Front plate with the text merged in | For single-color printing instead of the two files above |

None of the parts need supports.

## Two colors on a Bambu printer with AMS

Select `card-pocket-front.stl` and `card-pocket-text.stl` together in the import dialog. Bambu Studio should ask whether to load them as one object with multiple parts; answer yes, then assign a second filament to the text part (right-click > Change Filament). This is based on user reports and a university lab guide, not official Bambu documentation, so check the filament of each part after import. The color change only happens in the top 0.6 mm (3 layers at 0.2 mm), so there is little purge waste.

## Assembly

Put the front plate face up onto the walls; the 5 pegs go into the holes underneath. The holes are 0.2 mm larger per side than the pegs, so glue the parts (for example with superglue) on the wall tops.

## Regenerate

```
openscad -D 'part="back"' -o card-pocket-back.stl card-pocket.scad
openscad -D 'part="front"' -o card-pocket-front.stl card-pocket.scad
openscad -D 'part="text"' -o card-pocket-text.stl card-pocket.scad
openscad -D 'part="front_single"' -o card-pocket-front_single.stl card-pocket.scad
```
The text uses the font "Liberation Sans:style=Bold". If it is not installed, OpenSCAD falls back to another font.
