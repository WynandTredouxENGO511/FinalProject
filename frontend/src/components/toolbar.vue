<template>
  <v-app id="inspire" class="overflow-hidden">
    <v-navigation-drawer v-model="drawer" dark app>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              <h1>Visualize Crime Data</h1>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-divider></v-divider>
        <v-expansion-panels multiple>
          <v-expansion-panel>
            <v-expansion-panel-header>Filters</v-expansion-panel-header>
            <v-divider></v-divider>
            <!-- Selectors for filtering crime data -->
            <v-expansion-panel-content>
              <v-list dense>
                  <v-list-item-content>
                    <v-select :items="years" label="Years" outlined multiple></v-select>
                    <v-select :items="IncidentTypes" label="Incident Types" outlined multiple></v-select>
                  </v-list-item-content>
              </v-list>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-list>
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
    }),

    mounted() {
      //delete 
      eventBus.$on("foundHospital", data => {
        this.alert = "Nearest Hospital/Cliic from " + data.school + " is " + data.hospital + "!";
        this.snackbar = true;
      });

      //function to handle report form
      eventBus.$on("openForm", data => {
        this.dialog = true;
        this.dialogTitle = "Report an Incident the ".concat(data.Cname, " community");
        this.community = data.Cname;
      });
    },
    methods: {
      onSubmit() {
        // check that required field is filled (date is always filled by default)
        if (this.IncidentType == '') {
          alert("Please select an Incident Type");
          return false;
        }

        console.log(this.IncidentType);
        console.log(this.date);
        console.log(this.comment);
        const path = 'http://localhost:5000/';
        const payload = {
          type: this.IncidentType,
          date: this.date,
          community: this.community,
          comment: this.comment,
        };
        axios.post(path, payload);
        this.IncidentType = '';
        this.comment = '';
        this.date = new Date().toISOString().substr(0, 10);
        this.dialog = false;
        return true;
      }
    }
  };
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
</style>