// Pin-on business-card pocket, ONE PIECE printed standing up (as it hangs) – perryvillestay.com
// Holds about 20 US business cards (3.5 x 2 in) next to a flyer; hangs with two push pins.
// Print orientation: as exported – pocket bottom on the bed, back plate and front wall vertical. No supports.
// Coordinates: x = width, y = depth (back plate at y = 0, front faces +y), z = up.
//
//   part = "pocket"      -> the pocket with raised text, single color (default)
//   part = "body"        -> pocket without text (for a two-color print together with "text")
//   part = "text"        -> raised text only (second color; costs many filament changes on a vertical face)
// All sizes in mm.

part = "pocket";

card_w     = 88.9;   // 3.5 in
card_h     = 50.8;   // 2 in
clearance  = 1.5;    // per side
pocket_d   = 9;      // inner depth front-to-back: ~20 cardstock cards
wall       = 1.2;    // side walls, front wall and pocket floor (about 3 lines with a 0.4 mm nozzle)
back_t     = 1.2;    // back plate thickness
front_h    = 30;     // height of the pocket (front wall and side walls)
back_h     = card_h + wall;  // back plate as high as a standing card; pin it up first, then add cards
pin_d      = 2.2;    // push-pin hole diameter
pin_z      = back_h - 6;     // pin hole height from the bottom (near the top corners)
pin_inset  = 10;     // pin hole distance from the side edges
notch_r    = 11;     // thumb notch radius in the front wall
text_h     = 0.6;    // raised text height
font_b     = "Liberation Sans:style=Bold";
line1      = "Work stays in Perryville";
line2      = "perryvillestay.com";

inner_w = card_w + 2 * clearance;
outer_w = inner_w + 2 * wall;
depth   = back_t + pocket_d + wall;
$fn = 64;

module body() {
  difference() {
    union() {
      cube([outer_w, back_t, back_h]);                       // back plate
      cube([outer_w, depth, front_h]);                       // pocket block
    }
    translate([wall, back_t, wall]) cube([inner_w, pocket_d, front_h]);                     // card slot, open at the top
    translate([outer_w/2, depth + 1, front_h]) rotate([90, 0, 0]) cylinder(r = notch_r, h = wall + 2);  // thumb notch in the front wall
    for (x = [pin_inset, outer_w - pin_inset])
      translate([x, -1, pin_z]) rotate([-90, 0, 0]) cylinder(d = pin_d, h = back_t + 2);   // pin holes
  }
}

module text_part() {
  // on the front face, read from the front
  translate([outer_w/2, depth, 0]) rotate([90, 0, 180])
    linear_extrude(text_h) {
      translate([0, 12.6]) text(line1, size = 4.6, font = font_b, halign = "center");
      translate([0, 4.2])  text(line2, size = 6.4, font = font_b, halign = "center");
    }
}

if (part == "body") body();
else if (part == "text") text_part();
else union() { body(); text_part(); }
