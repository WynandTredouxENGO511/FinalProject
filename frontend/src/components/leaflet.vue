<template>
  <v-container class="fill-height" fluid id="map-container" position="static"></v-container>
</template>

<script>
import leaflet from "leaflet";
import { eventBus } from "../main.js";
import "leaflet.markercluster";
import axios from "axios";
import * as turf from "@turf/turf";

export default {
  name: "mymap",

  data() {
    return {
      leaf: null, //Interactive map
      cluster: null,
      schools: null,
      hospitals: null,
      path: null
    };
  },

  // api for schools: https://data.calgary.ca/resource/fd9t-tdn2.geojson
  // api for hospitals:
  mounted() {
  
    this.initMap();

    eventBus.$on("clear", () => {
      if (this.path != null) {
        this.leaf.removeLayer(this.path);
      }
    });
  },

  methods: {
    //initializes leaflet map
    initMap() {
      //OSM tile layer
      var OSMtile = new leaflet.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
          attribution:
            'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
          maxZoom: 18
        }
      );
      //satellite tile layer
      var satellite = new leaflet.tileLayer(
        "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}",
        {
          attribution:
            'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
          maxZoom: 18,
          id: "mapbox.satellite",
          accessToken:
            "pk.eyJ1IjoiYWEtdmFyaXl1biIsImEiOiJjanZzYmhja2QxM2l5NGFvOHpqdXhiNDJvIn0.ez9bRvvx0eg9RZVmjiTPpQ"
        }
      );

      //leaflet map
      this.leaf = new leaflet.map("map-container", {
        center: [51.0839, -114.1439],
        zoom: 13,
        layers: [OSMtile]
      });
      //adds scale bar
      leaflet.control.scale().addTo(this.leaf);
      //adds layer control to the map
      var defaultTile = { OpenStreetMap: OSMtile, Satellite: satellite };
      leaflet.control.layers(defaultTile).addTo(this.leaf);

      let _this = this;

      // add schools to map
      axios
        .get("https://data.calgary.ca/resource/fd9t-tdn2.geojson")
        .then(function(response) {
          _this.schools = response.data.features;
          //custom school icon
          var schoolMarker = leaflet.divIcon({
            className: "marker",
            iconSize: [32, 32]
          });
          var geoLayer = leaflet.geoJson(_this.schools, {
            pointToLayer: function(feature, latlng) {
              return leaflet
                .marker(latlng, { icon: schoolMarker })
                .on("click", onClick);
            }
          });

          //bind popup to all markers
          _this.cluster = leaflet.markerClusterGroup();
          _this.cluster.addLayer(geoLayer);

          _this.cluster.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });
          _this.leaf.addLayer(_this.cluster);
        })
        .catch(function(error) {
          console.log(error);
        });

      //add hospitals and clinics to the map
      axios
        .get(
          "https://data.calgary.ca/resource/x34e-bcjz.geojson?$where=type = 'Hospital' OR type = 'PHS Clinic'"
        )
        .then(function(response) {
          _this.hospitals = response.data.features;
          //custom hospital icon
          var hospMarker = leaflet.divIcon({
            className: "marker2",
            iconSize: [32, 32]
          });
          var geoLayer2 = leaflet.geoJson(_this.hospitals, {
            pointToLayer: function(feature, latlng) {
              return leaflet.marker(latlng, { icon: hospMarker });
            }
          });

          geoLayer2.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });
          _this.leaf.addLayer(geoLayer2);
        })
        .catch(function(error) {
          console.log(error);
        });

      //onclick function when users click on school marker
      function onClick(e) {
        var school = turf.point([e.latlng.lng, e.latlng.lat]);
        var hosp = [];
        for (var i = 0; i < _this.hospitals.length; ++i) {
          hosp.push(turf.point(_this.hospitals[i].geometry.coordinates));
        }
        hosp = turf.featureCollection(hosp);
        var nearesthospital = turf.nearestPoint(school, hosp);
        //if line already exists, remove it before adding new one
        if (_this.path != null) {
          _this.leaf.removeLayer(_this.path);
        }
        // fix distance and create tooltip
        var tooltip;
        if ( nearesthospital.properties.distanceToPoint < 1.0) {
          tooltip = "Distance is " + (nearesthospital.properties.distanceToPoint * 1000).toFixed(2) + " m";
        } else {
          tooltip = "Distance is " + nearesthospital.properties.distanceToPoint.toFixed(2) + " km";
        }

        _this.path = leaflet
          .polyline(
            [
              [e.latlng.lat, e.latlng.lng],
              [
                nearesthospital.geometry.coordinates[1],
                nearesthospital.geometry.coordinates[0]
              ]
            ],
            { color: "red" }
          )
          .bindTooltip(tooltip)
          .addTo(_this.leaf);
        // get name of hospital
        var name;
        for (i = 0; i < _this.hospitals.length; i++) {
          if (
            nearesthospital.geometry.coordinates[0] ==
              _this.hospitals[i].geometry.coordinates[0] &&
            nearesthospital.geometry.coordinates[1] ==
              _this.hospitals[i].geometry.coordinates[1]
          ) {
            name = _this.hospitals[i].properties.name;
            break;
          }
        }
        eventBus.$emit("foundHospital", {
          school: e.target.feature.properties.name,
          hospital: name
        });
        _this.leaf.fitBounds(_this.path.getBounds());
      }
    } //---- end of map initialization ----
  }
};
</script>

<style scoped>
@import "../../node_modules/leaflet.markercluster/dist/MarkerCluster.css";
@import "../../node_modules/leaflet.markercluster/dist/MarkerCluster.Default.css";

#map-container {
  z-index: 1;
}
</style>
