mkdir -p .data

wget -O ".data/prices_pl.csv" "https://drive.google.com/uc\?id\=1wU_zVNQoMtwc7XX1W3WZIbfBa5tuZ5oG\&export\=download"

weather_link_template="https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/terminowe/synop/"
for year in {2016..2022}
do
    wget -rkcN -np -nd -R "index.html*" -P ".data/weather/$year" "$weather_link_template/$year/"
done

unzip ".data/**/*.zip"
