# Third-party asset notices

This inventory records what can and cannot be established from the repository
as of 2026-07-26. It is not a substitute for the original license files.

## Verified item

| Files | Work and author | Source | License |
|---|---|---|---|
| `assets/fonts/PixelTimesNewRoman.ttf` | Pixel Times New Roman by Wesley Mitchell | [BitFontMaker2 gallery](https://www.pentacom.jp/pentacom/bitfontmaker2/gallery/?id=5231) | Public Domain, as stated on the source page |

## Declared sources with incomplete file-level provenance

The README historically names [CraftPix](https://craftpix.net/),
[itch.io](https://itch.io/), and
[Eder Munizz](https://edermunizz.itch.io/) as sources. The repository history
does not identify which files came from which product page and contains no
download receipts or original license texts.

This affects:

- `assets/images/backgrounds/`
- `assets/images/fighters/`
- `assets/images/icons/skull.png`
- `assets/fonts/HelvetiPixel.ttf`

CraftPix publishes general license information, but that does not prove that a
specific repository file came from a particular CraftPix product. itch.io is a
hosting platform whose creators set licenses per project; the platform terms
alone do not grant a uniform asset license. The Eder Munizz profile link does
not identify the exact downloaded work.

## Repository-created material

Files under `assets/images/ss/` are project screenshots recorded in the Git
history. `assets/images/backgrounds/controls.png` also contains project-specific
control presentation, but its underlying visual components are not documented
well enough to make a broader ownership claim.

## Release blocker

Before publishing a binary release, the project owner should:

1. map every image/font to its exact product or author page;
2. save the license text or receipt that applied when it was downloaded;
3. confirm that redistribution inside an executable bundle is permitted;
4. choose and add a license for the project's own source code.

Until then, generated packages are suitable for local verification, but their
public redistribution status is not established.
