<template>
  <v-app id="inspire" class="overflow-hidden">
    <v-navigation-drawer v-model="drawer" dark app style="z-index: 204;">
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              <h1>Visualize Crime Data</h1>
              <v-switch v-model="filter2" label="Multiple Filters"></v-switch>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-divider></v-divider>
        <v-expansion-panels multiple accordion style="z-index: 1000;" v-model="expand">
          <v-expansion-panel>
            <v-expansion-panel-header>Filter 1 (Left)</v-expansion-panel-header>
            <v-divider></v-divider>
            <!-- Selectors for filtering crime data -->
            <v-expansion-panel-content>
              <v-list-item-content>
                <v-select :items="years" label="Years" outlined multiple v-model="filterLeft.year"></v-select>
                <v-select :items="IncidentTypes" label="Incident Types" outlined multiple v-model="filterLeft.incident">
                </v-select>
                <v-autocomplete :items="communities" item-text="properties.name" label="Communities" outlined multiple
                  dense v-model="filterLeft.community"></v-autocomplete>
              </v-list-item-content>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <!-- 2nd expansion panel for optional 2nd filter -->
          <v-expansion-panel :disabled="!filter2">
            <v-expansion-panel-header>Filter 2 (Right)</v-expansion-panel-header>
            <v-divider></v-divider>
            <v-expansion-panel-content>
              <v-list dense>
                <v-list-item-content>
                  <v-select :items="years" label="Years" outlined multiple v-model="filterRight.year"></v-select>
                  <v-select :items="IncidentTypes" label="Incident Types" outlined multiple
                    v-model="filterRight.incident"></v-select>
                  <v-autocomplete :items="communities" item-text="properties.name" label="Communities" outlined multiple
                    dense v-model="filterRight.community"></v-autocomplete>
                </v-list-item-content>
              </v-list>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-list>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title class="pb-2">
              <h1>Toggle Heatmaps</h1>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-content>
            <v-switch v-model="heatLeft" label="Left" @change="toggleHeatLeft"></v-switch>
            <v-switch v-model="heatRight" label="Right" @change="toggleHeatRight"></v-switch>
          </v-list-content>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-col align="center">
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-btn color="blue" @click.stop="verify" v-on="on"> UPDATE</v-btn>
          </template>
          <span>Submit data</span>
        </v-tooltip>
      </v-col>
      <v-col align="center">
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-btn color="red" @click="off" v-on="on">clear</v-btn>
          </template>
          <span>Clear all data</span>
        </v-tooltip>
      </v-col>
    </v-navigation-drawer>
    <!-- Top Nav Bar -->
    <v-app-bar app color="Black" dark class="pl-2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title class="font-weight-black">Police things add cool title here</v-toolbar-title>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon dark v-on="on" @click="about = !about">
            <v-icon large> mdi-information</v-icon>
          </v-btn>
        </template>
        <span>Learn more about the app!</span>
      </v-tooltip>

      <v-dialog v-model="about" width="500" scrollable>
        <v-card>
          <v-card-title class="headline grey lighten-2" primary-title>About NHIYA!</v-card-title>

          <v-card-text class="pt-2">
            <p style="font-size:110%;">Welcome to "Nice Hospitals in Your Area" or NHIYA for short. Are you a sick
              student looking to get better? Broken leg? Bad cough?
              Well now you can find hospitals and clinics closest to your school! So what are you waiting for? These
              hospitals are
              desperately looking to patch you up!</p>
            <br />
            <h3 style="text-align:center;">Thank You for Using NHIYA!</h3>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="about = false" icon>
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-app-bar>
    <!-- Leaflet Map -->
    <!-- Template for crime form submission -->

    <v-dialog v-model="dialog" fullscreen hide-overlay transition="dialog-bottom-transition">
      <v-card>
        <v-toolbar dark color="indigo">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>{{ dialogTitle }}</v-toolbar-title>
        </v-toolbar>

        <div class="register-box">
          <v-form>
            <h2>Incident Type</h2>
            <v-select :items="IncidentTypes" :rules="[v => !!v || 'Item is required']"
              label="Select an Inident Category" required v-model="IncidentType"></v-select>

            <h2>Incident Date</h2>
            <v-menu ref="menu" v-model="menu" :close-on-content-click="false" :return-value.sync="date"
              transition="scale-transition" offset-y min-width="290px">
              <template v-slot:activator="{ on }">
                <v-text-field v-model="date" prepend-icon="event" :rules="[v => !!v || 'Item is required']" required
                  v-on="on"></v-text-field>
              </template>
              <v-date-picker v-model="date" no-title scrollable>
                <v-spacer></v-spacer>
                <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
                <v-btn text color="primary" @click="$refs.menu.save(date)">OK</v-btn>
              </v-date-picker>
            </v-menu>

            <h2>Comment</h2>
            <v-textarea placeholder="(Optional)" auto-grow v-model="comment" />
            <v-btn dark color="blue" class="mr-4" v-on:click="onSubmit">submit</v-btn>
          </v-form>
        </div>
      </v-card>
    </v-dialog>
    <!-- CHART LEFT  -->

    <v-dialog v-model="cardLeft" hide-overlay persistent no-click-animation>
      <v-card style="position: absolute; bottom: 0; left: 0; z-index: 2;" width="600" height="300">
        <canvas id="leftChart"></canvas>
      </v-card>
    </v-dialog>
    <!-- CHART RIGHT -->
    <v-dialog v-model="cardRight" hide-overlay persistent no-click-animation>
      <v-card style="position: absolute; bottom: 0; right: 0;  z-index: 2;" width="600" height="300">
        <canvas id="rightChart"></canvas>
      </v-card>
    </v-dialog>

    <v-content>
      <v-container class="fill-height pa-0 ma-0" fluid>
        <mymap />
      </v-container>
    </v-content>
    <v-snackbar v-model="snackbar" color="red" :timeout=15000>
      {{ alert }}
      <v-btn color="black" text @click="snackbar = false">Close</v-btn>
    </v-snackbar>

  </v-app>
</template>

<script>
  import mymap from "./leaflet";
  import Chart from 'chart.js';
  import {
    eventBus
  } from '../main';
  import axios from "axios";

  export default {
    name: "toolbar",
    components: {
      mymap
    },
    props: {
      source: String
    },
    data: () => ({
      sheet: false,
      alert: "If you are seeing this, contact the developer",
      about: false,
      snackbar: false,
      dialog: false,
      dialogTitle: "",
      community: "",
      IncidentTypes: [
        "Theft From Vehicle", "Theft of Vehicle", "Break & Enter - Commercial",
        "Assault (Non-domestic)", "Break & Enter - Dwelling", "Violence Other (Non-domestic)",
        "Break & Enter - Other Premises", "Street Robbery", "Commercial Robbery", "Other"
      ],
      date: new Date().toISOString().substr(0, 10),
      IncidentType: '',
      comment: '',
      menu: false,
      drawer: false,
      years: [2017, 2018, 2019, 2020],
      communities: null,
      filter2: false,
      captchaScore: 0,
      filterLeft: {
        year: [],
        incident: [],
        community: [],
      },
      filterRight: {
        year: [],
        incident: [],
        community: [],
        chart: null,
      },
      chartLeft: null,
      chartRight: null,
      cardLeft: false,
      cardRight: false,
      heatLeft: false,
      heatRight: false,
      expand: [],
    }),

    mounted() {
      eventBus.$on("foundHospital", data => {
        this.alert = "Nearest Hospital/Clinic from " + data.school + " is " + data.hospital + "!";
        this.snackbar = true;
      });

      //function to handle report form
      eventBus.$on("openForm", data => {
        this.dialog = true;
        this.dialogTitle = "Report an Incident the ".concat(data.Cname, " community");
        this.community = data.Cname;
      });

      //function to get communities geojson from leaflet.vue
      eventBus.$on("setCommunities", data => {
        this.communities = data;
      });

      //set captcha score
      eventBus.$on("setScore", data => {
        this.captchaScore = data;
      });
    },

    methods: {
      onSubmit() {
        // check that required field is filled (date is always filled by default)
        if (this.IncidentType == '') {
          alert("Please select an Incident Type");
          return false;
        }
        eventBus.$emit("getScore");
        console.log(this.IncidentType);
        console.log(this.date);
        console.log(this.comment);
        console.log(this.captchaScore)
        const path = 'http://localhost:5000/';
        const payload = {
          type: this.IncidentType,
          date: this.date,
          community: this.community,
          comment: this.comment,
          score: this.captchaScore,
        };

        axios.post(path, payload).then(function (response) {
            if (response.data.status == 'fail') {
              console.log(response.data.status);
              console.log(response.data.comment);
              alert('Error: Cannot submit form because your reCaptcha score is too low. Are you a bot?')
              return false;
            }
          })
          .catch(function (error) {
            console.log(error);
            alert('Error: Could not verify reCaptcha score. Submission failed');
          });

        this.IncidentType = '';
        this.comment = '';
        this.date = new Date().toISOString().substr(0, 10);
        this.dialog = false;
        return true;
      },

      verify() {
        if (this.filterLeft.year.length == 0) {
          alert("Year Field in Filter Not Selected!");
        } else if (this.filter2 && (this.filterLeft.year.length == 0 || this.filterRight.year.length == 0)) {
          alert("Year Field in Filter Not Selected!");
        } else {
          this.visualize();
        }
      },

      visualize() {
        // QUERY THINGS
        this.expand = [];
        this.heatLeft = true;
        console.log('visualize');
        const path = 'http://localhost:5000/query';
        let _this = this;

        //variables to count crime LEFT SIDE
        var month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        var crimeCountLeft;
        (crimeCountLeft = []).length = this.filterLeft.year.length * 12;
        crimeCountLeft.fill(0);
        var crimeLeftData;
        // RIGHT SIDE 
        if (this.filterRight.year.length != 0) {
          this.heatRight = true;
          var crimeCountRight;
          (crimeCountRight = []).length = this.filterRight.year.length * 12;
          crimeCountRight.fill(0);
          var crimeRightData;
        }


        // always submit left query
        axios.get(path, {
            params: {
              incident: JSON.stringify(this.filterLeft.incident),
              date: JSON.stringify(this.filterLeft.year),
              community: JSON.stringify(this.filterLeft.community),
            }
          })
          .then(function (response) {
            //console.log(response); assuming one year
            //sort years by numerical order in case user doesn't follow numerical order
            var years = _this.filterLeft.year.sort();
            years = years.map(String);

            for (var i = 0; i < response.data.data.length; i++) {
              for (var j = 0; j < month.length; j++) {
                var yes = 0;
                //find the month in date
                if (response.data.data[i].date.search(month[j]) != -1) {
                  for (var h = 0; h < years.length; h++) {
                    //find the year in date 
                    if (response.data.data[i].date.search(years[h]) != -1) {
                      crimeCountLeft[j + h * 12] += response.data.data[i].count;
                      yes = 1;
                      break;
                    }
                  }
                  if (yes) break;
                }

              }
            }
            //create chart data 
            var sets = _this.makeData(crimeCountLeft, years);
            //console.log(sets);
            crimeLeftData = {
              type: 'line',
              data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: sets
              },
              options: {
                responsive: true,
                lineTension: 1,
                scales: {
                  yAxes: [{
                    ticks: {
                      beginAtZero: true,
                      padding: 25,
                    }
                  }]
                }
              }
            };

            //console.log(crimeCount);
            eventBus.$emit("setVisData", ['left', response]);
          })
          .catch(function (error) {
            console.log(error);
          });
        if (this.filter2) {
          // submit right query if enabled
          axios.get(path, {
              params: {
                incident: JSON.stringify(this.filterRight.incident),
                date: JSON.stringify(this.filterRight.year),
                community: JSON.stringify(this.filterRight.community),
              }
            })
            .then(function (response) {
              var years = _this.filterRight.year.sort();
              years = years.map(String);

              for (var i = 0; i < response.data.data.length; i++) {
                for (var j = 0; j < month.length; j++) {
                  var yes = 0;
                  //find the month in date
                  if (response.data.data[i].date.search(month[j]) != -1) {
                    for (var h = 0; h < years.length; h++) {
                      //find the year in date 
                      if (response.data.data[i].date.search(years[h]) != -1) {
                        crimeCountRight[j + h * 12] += response.data.data[i].count;
                        yes = 1;
                        break;
                      }
                    }
                    if (yes) break;
                  }

                }
              }
              //create chart data 
              var sets = _this.makeData(crimeCountRight, years);
              //console.log(sets);
              crimeRightData = {
                type: 'line',
                data: {
                  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                  datasets: sets
                },
                options: {
                  responsive: true,
                  lineTension: 1,
                  scales: {
                    yAxes: [{
                      ticks: {
                        beginAtZero: true,
                        padding: 25,
                      }
                    }]
                  }
                }
              }
              eventBus.$emit("setVisData", ['right', response]);
            })
            .catch(function (error) {
              console.log(error);
            });
        }

        // display charts 
        this.cardLeft = true;
        setTimeout(function () {
          _this.createChart('leftChart', crimeLeftData);
        }, 2000);

        if (this.filter2) {
          this.cardRight = true;
          setTimeout(function () {
            _this.createChart('rightChart', crimeRightData);
          }, 2000);
        }
      },
      //function to DELETE your soul
      off() {
        this.expand = [];
        //clear charts and reset variables
        this.filterLeft.year = [];
        this.filterLeft.community = [];
        this.filterLeft.incident = [];

        this.filterRight.year = [];
        this.filterRight.community = [];
        this.filterRight.incident = [];

        this.cardLeft = false;
        this.cardRight = false;

        this.heatLeft = false;
        this.heatRight = false;
        // clear heatmaps
        eventBus.$emit("clearheatmaps");
      },
      //function to create chart
      createChart(chartId, chartData) {
        console.log(chartData);
        const ctx = document.getElementById(chartId);
        const myChart = new Chart(ctx, {
          type: chartData.type,
          data: chartData.data,
          options: chartData.options,
        });
        this.chart = myChart;
      },

      //function to separate data in sets per year
      makeData(crime, years) {
        //console.log(crime);
        //standard background colors and borders
        //red, orange, green, teal
        var backColor = ['rgba(255, 99, 132, 0.2)', 'rgba(255, 162, 0,0.2)', 'rgba(141, 247, 42,0.2)',
          'rgba(0, 128, 129, 0.2)'
        ];
        var bordColor = ['rgba(255, 99, 132, 1)', 'rgba(255, 162, 0,1)', 'rgba(141, 247, 42,1)',
          'rgba(0, 128, 129, 1)'
        ];
        var sets = [];
        for (var i = 0; i < crime.length / 12; i++) {
          const temp = {
            label: years[i],
            data: crime.slice(i * 12, (i + 1) * 12),
            backgroundColor: backColor[i],
            borderColor: bordColor[i],
            borderWidth: 1
          };
          sets.push(temp);
        }
        return sets;
      },
      toggleHeatLeft() {
        eventBus.$emit("heatL", this.heatLeft);
      },
      toggleHeatRight() {
        eventBus.$emit("heatR", this.heatRight);
      },
    },
  }
</script>


<style scoped>
  .date-range {
    padding-left: 30%;
    padding-right: 30%;
  }

  .sheets {
    opacity: 0.6;
  }

  .sheets:hover {
    opacity: 1;
  }

  .tool {
    z-index: 1000;
  }

  .card-chart {
    z-index: 1000;
  }
</style>