#!/usr/bin/env sh
# Crop and re-encode the Studio captures for the web. Needs ffmpeg. Run from anywhere: sh tools/images.sh
# Raw captures are 1912x688 (Studio viewport, HUD hidden). The Roblox menu button sits in the top-left
# 250x82 corner of every raw frame, so every crop below stays clear of it.
set -e
RAW=/d/GROWIN/RobloxProject/store-assets/2026-11-03-site/raw
S=/d/GROWIN/RobloxProject/store-assets
O="$(dirname "$0")/../static/img"
P="$(dirname "$0")/../static/press"
mkdir -p "$O" "$P"

# name  source  crop w:h:x:y  (web width)
crop() {
  ffmpeg -hide_banner -loglevel error -y -i "$RAW/$2.png" -vf "crop=$3,scale=$4:-2" -c:v libwebp -quality 82 "$O/$1.webp"
  ffmpeg -hide_banner -loglevel error -y -i "$RAW/$2.png" -vf "crop=$3" -q:v 2 "$P/$1.jpg"
}
crop hero          hero_c              1652:684:260:0    1652
crop hero-mobile   hero_c              760:684:560:0     760
crop riot          riot_lane_8         1216:684:340:0    1216
crop boss-sky      boss_constellation  1066:600:0:82     1066
crop night-garden  night_garden_boss   1216:684:340:0    1216
crop pier          pier_islet          1216:684:600:0    1216
crop constellation constellation_night 1216:684:342:0    1216
crop lane          lane_dusk           1216:684:340:0    1216

# Social card (Open Graph) 1200x630 from the hero.
ffmpeg -hide_banner -loglevel error -y -i "$RAW/hero_c.png" -vf "crop=1302:684:330:0,scale=1200:630" -q:v 3 "$O/og.jpg"

# Icon, favicon and pass art from the store assets.
w() { ffmpeg -hide_banner -loglevel error -y -i "$1" -vf "scale=$3:-2" -c:v libwebp -quality 80 "$O/$2.webp"; }
w "$S/2026-10-18-icon/final/icon_A_secrets.png" icon 512
w "$S/2026-11-03-styles/final/wind_staff_pass.png" pass-wind-staff 300
w "$S/2026-11-03-styles/final/seed_rain_pass.png"  pass-seed-rain 300
ffmpeg -hide_banner -loglevel error -y -i "$S/2026-10-18-icon/final/icon_A_secrets.png" -vf "scale=64:64" "$O/favicon.png"
cp "$S/2026-10-18-icon/final/icon_A_secrets.png" "$P/icon.png"
echo "images done"
