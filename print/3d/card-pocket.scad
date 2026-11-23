// Pin-on business-card pocket for bulletin boards – perryvillestay.com
// Holds about 20 US business cards (3.5 x 2 in) next to a flyer; hangs with two push pins.
//
// Two parts, both printed flat without supports, then glued (pegs align them):
//   part = "back"  -> back plate with pin holes + U-shaped walls and pegs. Print lying on its back.
//   part = "front" -> front plate with thumb notch, printed face up; blind holes for the pegs underneath.
//   part = "text"  -> raised text on top of the front plate, as a separate body for a second AMS color.
//   part = "front_single" -> front plate with the text merged, for single-color printing.
//   part = "assembly" -> preview only.
// All sizes in mm.

part = "assembly";

card_w     = 88.9;   // 3.5 in
card_h     = 50.8;   // 2 in
clearance  = 1.5;    // per side
pocket_d   = 9;      // inner depth front-to-back: ~20 cardstock cards
wall       = 4;      // side and bottom wall width (wide enough for the pegs)
back_t     = 2.4;    // back plate thickness
front_t    = 2.4;    // front plate thickness
front_h    = 32;     // front plate height (covers the lower part of the cards)
back_h     = 72;     // back plate height (pin holes above the cards)
pin_d      = 2.2;    // push-pin hole diameter
pin_y      = 64;     // pin hole height from the bottom
pin_inset  = 12;     // pin hole distance from the side edges
notch_r    = 11;     // thumb notch radius in the front plate
peg_d      = 2.4;    // alignment pegs on the wall tops
peg_h      = 1.4;
hole_d     = 2.8;    // matching blind holes in the front plate
hole_depth = 1.7;
text_h     = 0.6;    // raised text height
font_b     = "Liberation Sans:style=Bold";
label      = "perryvillestay.com";
label_size = 7.5;  // largest size that leaves a few mm on each side

inner_w = card_w + 2 * clearance;
outer_w = inner_w + 2 * wall;
$fn = 64;

// peg positions (x, y) on the wall tops: two per side wall, one in the middle of the bottom wall
pegs = [[wall/2, 8], [wall/2, front_h - 6], [outer_w - wall/2, 8], [outer_w - wall/2, front_h - 6], [outer_w/2, wall/2]];

module back() {
  difference() {
    union() {
      cube([outer_w, back_h, back_t]);                                   // back plate
      translate([0, 0, back_t]) difference() {                             // U-shaped walls
        cube([outer_w, front_h, pocket_d]);
        translate([wall, wall, -1]) cube([inner_w, front_h, pocket_d + 2]);
      }
      for (p = pegs) translate([p[0], p[1], back_t + pocket_d]) cylinder(d = peg_d, h = peg_h);
    }
    for (x = [pin_inset, outer_w - pin_inset]) translate([x, pin_y, -1]) cylinder(d = pin_d, h = back_t + 2);
  }
}

module front_plate() {
  difference() {
    cube([outer_w, front_h, front_t]);
    translate([outer_w/2, front_h, -1]) cylinder(r = notch_r, h = front_t + 2);   // thumb notch
    for (p = pegs) translate([p[0], p[1], -0.01]) cylinder(d = hole_d, h = hole_depth);  // blind holes, open underneath
  }
}

module front_text() {
  translate([outer_w/2, 0, front_t]) linear_extrude(text_h) {
    translate([0, 8]) text(label, size = label_size, font = font_b, halign = "center");
  }
}

if (part == "back") back();
else if (part == "front") front_plate();
else if (part == "text") front_text();
else if (part == "front_single") union() { front_plate(); front_text(); }
else {  // assembly preview: front plate (face up) sitting on the walls
  back();
  translate([0, 0, back_t + pocket_d]) { color("white") front_plate(); color("navy") front_text(); }
  % translate([wall + clearance, wall, back_t + 1]) cube([card_w, card_h, 7]);    // cards (ghost)
}
