<template>
  <v-app id="inspire" class="overflow-hidden">
    <!-- Top Nav Bar -->
    <v-app-bar app color="red" dark class="pl-2">
      <v-icon large>mdi-hospital</v-icon>
      <v-toolbar-title class="font-weight-black">NHIYA</v-toolbar-title>
      <v-spacer />

      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn text dark v-on="on" @click="clearpath();">
            CLEAR
          </v-btn>
        </template>
        <span>Clear path from map</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon  dark v-on="on" @click="about = !about">
            <v-icon large> mdi-information</v-icon>
          </v-btn>
        </template>
        <span>Learn more about the app!</span>
      </v-tooltip>

      <v-dialog v-model="about" width="500" scrollable>
        <v-card>
          <v-card-title class="headline grey lighten-2" primary-title>About NHIYA!</v-card-title>

          <v-card-text class="pt-2">
            <p
              style="font-size:110%;"
            >Welcome to "Nice Hospitals in Your Area" or NHIYA for short. Are you a sick student looking to get better? Broken leg? Bad cough? 
            Well now you can find hospitals and clinics closest to your school! So what are you waiting for? These hospitals are 
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
import { eventBus } from '../main';

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
  }),

  mounted() {
    eventBus.$on("foundHospital", data => {
      this.alert = "Nearest Hospital/Cliic from " + data.school + " is " + data.hospital + "!";
      this.snackbar = true;
    });
  },
  methods: {
    clearpath() {
      eventBus.$emit("clear");
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