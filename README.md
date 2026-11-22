# perryvillestay.com

Landing page for the Airbnb listing "German-Inspired Home in Perryville" (Perryville, Missouri), operated by Lenk Innovations LLC.

- Static HTML/CSS, no build step, no cookies. Visits are counted with Cloudflare Web Analytics (cookie-free; enabled 2026-11-22 for the zone, the beacon is injected automatically by Cloudflare).
- Hosted on Cloudflare Pages (production branch `main`, output directory `/`).
- All booking happens on Airbnb: https://www.airbnb.com/rooms/886866055139580236
- Deliberately no prices on the page (only the weekly 25 % / monthly 30 % discounts and the 32-night county tax exemption) – keep these in sync with the Airbnb settings and the family knowledge base.
- Photos in `images/` are the owners' own listing photos (1440 px and 800 px versions).

## QR codes on print material

Each printed format has its own QR code so Web Analytics can show which one gets scanned (Web Analytics records paths but no query strings, so `?utm=` tags would not work).

- `/q/<code>` is served as the home page (`_redirects`: `/q/* / 200`, canonical link in `_headers`); the old `/flyer` and `/card` codes work the same way.
- Codes: `flyer` (color Letter flyer), `bw` (black-and-white flyer), `half` (half-page flyer), `rack` (rack card), `photo` (4x6 photo card), `card` (all business cards); locations `tg`, `mercy`, `gilster`, `air` (airport and West Star), `chamber` (Chamber and Welcome Center), `shrine`. Location business cards use `card-<location>`, the Shrine rack card `rack-shrine`.
- Location versions: `print/flyer.html?qr=<location>`, `print/cards.html?qr=<location>`, `print/cards-bw.html?paper=…&qr=<location>`, `print/cards-photo-4x6.html?qr=<location>`, `print/rack-card.html?qr=shrine`. Rendered files are in `print/locations/`. QR images are `print/qr-q-<code>.svg`. Location flyers name their own destination first in the drive-times footnote.
- Results: Cloudflare dashboard > Web Analytics > perryvillestay.com, filter or group by Path.
- Every printed page and card shows its code in small gray text in the bottom-right corner (read automatically from the QR image it uses), so printed piles can be told apart.

## Discounts in print

Print material deliberately shows no percentages ("Weekly discount", "Monthly discount", "Weekly & monthly discounts on Airbnb"), because the 25 % / 30 % discounts are a trial reviewed by the end of March 2027. The exact numbers appear only on the website. The 32-night county tax exemption is printed because it follows the county tax rules, not the trial.
