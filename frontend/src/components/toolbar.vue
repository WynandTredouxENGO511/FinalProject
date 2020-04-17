<template>
  <v-app id="inspire" class="overflow-hidden">
    <v-navigation-drawer v-model="drawer" dark app style="z-index: 1000;">
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
        <v-expansion-panels multiple accordion>
          <v-expansion-panel>
            <v-expansion-panel-header>Filter 1 (Left)</v-expansion-panel-header>
            <v-divider></v-divider>
            <!-- Selectors for filtering crime data -->
            <v-expansion-panel-content>
              <v-list dense>
                <v-list-item-content>
                  <v-select :items="years" label="Years" outlined multiple v-model="filterLeft.year"></v-select>
                  <v-select :items="IncidentTypes" label="Incident Types" outlined multiple
                    v-model="filterLeft.incident"></v-select>
                  <v-autocomplete :items="communities" item-text="properties.name" label="Communities" outlined multiple
                    dense v-model="filterLeft.community"></v-autocomplete>
                </v-list-item-content>
              </v-list>
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
      <v-col align="center">
        <v-btn color="blue" @click="visualize"> UPDATE</v-btn>
      </v-col>
      <v-col align="center">
        <v-btn color="red" @click="off">clear</v-btn>
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
    <v-dialog v-model="cardLeft" hide-overlay elevation="5" persistent no-click-animation>
      <v-card style="position: absolute; bottom: 0; left: 0;" width="500" height="300">
        <canvas id="planet-chart"></canvas>
      </v-card>
    </v-dialog>
    <!-- CHART RIGHT -->
    <v-dialog v-model="cardRight" hide-overlay elevation="5" persistent no-click-animation>
      <v-card style="position: absolute; bottom: 0; right: 0;" width="500" height="300">
        <canvas id="planet-chart2"></canvas>
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

  const planetChartData = {
    type: 'line',
    data: {
      labels: ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
      datasets: [{ // one line graph
          label: 'Number of Moons',
          data: [0, 0, 1, 2, 67, 62, 27, 14],
          backgroundColor: [
            'rgba(54,73,93,.5)', // Blue
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)',
            'rgba(54,73,93,.5)'
          ],
          borderColor: [
            '#36495d',
            '#36495d',
            '#36495d',
            '#36495d',
            '#36495d',
            '#36495d',
            '#36495d',
            '#36495d',
          ],
          borderWidth: 3
        },
        { // another line graph
          label: 'Planet Mass (x1,000 km)',
          data: [4.8, 12.1, 12.7, 6.7, 139.8, 116.4, 50.7, 49.2],
          backgroundColor: [
            'rgba(71, 183,132,.5)', // Green
          ],
          borderColor: [
            '#47b784',
          ],
          borderWidth: 3
        }
      ]
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
    }),

    watch: {
      filter2(newValue) {
        //called whenever filter2 changes
        if (newValue) { // if filter 2 is enabled
          //enable leaflet sideBySide
          eventBus.$emit("addsbs");
        } else {
          //disable leaflet sideBySide
          eventBus.$emit("clearsbs");
        }

      }
    },

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

      visualize() {
        let _this = this;
        this.cardLeft = true;
        setTimeout(function () {
          _this.createChart('planet-chart', planetChartData);
        }, 500);
        if (this.filter2) {
          this.cardRight = true;
          setTimeout(function () {
            _this.createChart('planet-chart2', planetChartData);
          }, 500);
        }
      },

      off() {
        //clear charts and reset variables
        this.filterLeft.year = [];
        this.filterLeft.community = [];
        this.filterLeft.incident = [];

        this.filterRight.year = [];
        this.filterRight.community = [];
        this.filterRight.incident = [];

        this.cardLeft = false;
        this.cardRight = false;
      },

      createChart(chartId, chartData) {
        const ctx = document.getElementById(chartId);
        const myChart = new Chart(ctx, {
          type: chartData.type,
          data: chartData.data,
          options: chartData.options,
        });
        this.chart = myChart;
      }

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