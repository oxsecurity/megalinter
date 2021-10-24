<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.5.0/chart.min.js"
  integrity="sha512-asxKqQghC1oBShyhiBwA+YgotaSYKxGP1rcSYTDrB0U6DxwlJjU59B67U8+5/++uFjcuVM8Hh5cokLjZlhm3Vg=="
  crossorigin="anonymous" referrerpolicy="no-referrer"></script>

<div>
  <canvas id="myChart"></canvas>
</div>

<script>
  const randomNum = () => Math.floor(Math.random() * (235 - 52 + 1) + 52);
  const randomRGB = () => `rgb(${randomNum()}, ${randomNum()}, ${randomNum()})`;
  fetch('https://raw.githubusercontent.com/megalinter/megalinter/master/.automation/generated/flavors-stats.json')
    .then(function (response) {
      if (!response.ok) {
        throw new Error("HTTP error, status = " + response.status);
      }
      return response.json();
    })
    .then(function (flavorsStats) {
      const labels = [];
      const dataSets = [];
      for (const flavor of Object.keys(flavorsStats)) {
        if (flavor === "dotnet") {
          continue ;
        }
        const flavorData = [];
        for (const dateStat of flavorsStats[flavor]) {
          const dateDay = dateStat[0].substring(0, 10);
          labels.push(dateDay);
          flavorData.push(dateStat[1])
        }
        const dataSet = {
            label: flavor,
            borderColor: randomRGB(),
            data: flavorData,
            yAxisID: 'y',
        };
        dataSets.push(dataSet);
      }
      const data = {
        labels: labels.filter((it, i, ar) => ar.indexOf(it) === i), // make unique
        datasets: dataSets
      };
      const config = {
        type: 'line',
        data: data,
        options: {
          responsive: true,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          stacked: false,
          plugins: {
            title: {
              display: true,
              text: 'Mega-Linter flavors stats'
            }
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
            }
          }
        },
      };
      var myChart = new Chart(
        document.getElementById('myChart'),
        config
      );
    });
</script>