<template>
  <v-container class="fill-height" fluid id="map-container" position="static"></v-container>
</template>

<script>
import leaflet from "leaflet";
import { eventBus } from "../main.js";
import "leaflet.markercluster";
import axios from "axios";
import * as turf from "@turf/turf";
import "leaflet-contextmenu";

export default {
  name: "mymap",

  data() {
    return {
      leaf: null, // Interactive map
      cluster: false,
      hospitals: null,
      fire: null,
      police: null,
      path: null,
      // emergancy station map layers
      hosplayer: null,
      fireLayer: null,
      policeLayer: null,
      // cluster layer
      emergcluster: null,
    };
  },

  mounted() {
  
    this.initMap();

    eventBus.$on("clear", () => {
      if (this.path != null) {
        this.leaf.removeLayer(this.path);
      }
    });

    eventBus.$on("ReloadEmerg", () => {
      console.log('Reload emergancy servies layers')
      if (this.hosplayer == null || this.fireLayer == null || this.policeLayer == null) {
        console.log("ReloadEmerg: Error, null layer");
        return;
      }

      // remove layers from map
      this.leaf.removeLayer(this.hosplayer);
      this.leaf.removeLayer(this.fireLayer);
      this.leaf.removeLayer(this.policeLayer);
      this.leaf.removeLayer(this.emergcluster);

      // re-add layers based on cluster option
      if (this.cluster){
        this.leaf.addLayer(this.emergcluster);
      }else{
        this.leaf.addLayer(this.hosplayer);
        this.leaf.addLayer(this.fireLayer);
        this.leaf.addLayer(this.policeLayer);
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
        zoom: 11,
        layers: [OSMtile],
        contextmenu: true,
            contextmenuWidth: 170,
            contextmenuItems: [{
                text: 'Show coordinates',
                callback: showCoordinates
            }, {
                text: 'Center map here',
                callback: centerMap
            }, {
                text: 'Report incident here',
                callback: ReportInc
            }, '-', {
                text: 'Zoom in',
                icon: 'https://img.icons8.com/metro/26/000000/zoom-in.png',
                callback: zoomIn
            }, {
                text: 'Zoom out',
                icon: 'https://img.icons8.com/metro/26/000000/zoom-out.png',
                callback: zoomOut
            },{
              text:'Cluster icons toggle: false',
              callback: clustertoggle
            }, '-', {
              text: 'Find Nearest Hospital',
              callback: NearestHosp
            }, {
              text: 'Find Nearest Police Station',
              callback: NearestPol
            }, {
              text: 'Find Nearest Fire Station',
              callback: NearestFire
            }]
      });

      let _this = this;

      // context menu items
        function showCoordinates(e) {
            var msg = ''.concat(e.latlng.lat, ', ', e.latlng.lng);
            alert(msg);
        }

        function centerMap(e) {
            _this.leaf.panTo(e.latlng);
        }

        function zoomIn() {
            _this.leaf.zoomIn();
        }

        function zoomOut() {
            _this.leaf.zoomOut();
        }

        function ReportInc(e) {
          // check which community the coordinate is in
          var point = turf.point([e.latlng.lng, e.latlng.lat]);
          var communityName = '';
          //console.log(point);
          //console.log(_this.communityB)
          for (var i = 0; i<_this.communityB.length; i++){
            if (turf.booleanContains(_this.communityB[i].geometry, point)){
              console.log(_this.communityB[i].properties.name);
              communityName = _this.communityB[i].properties.name;
              break;
            }
          }
          if (communityName == ''){
            alert("This website only supports reporting incidents within Calgary");
          }else{
            eventBus.$emit("openForm", {lat: e.latlng.lat, lng: e.latlng.lng, Cname: communityName});
          }
        }

        function NearestHosp(e){
          var point = turf.point([e.latlng.lng, e.latlng.lat]);
          var layer = _this.hospitals;
          Nearest(point, layer);
        }

        function NearestPol(e){
          var point = turf.point([e.latlng.lng, e.latlng.lat]);
          var layer = _this.police;
          Nearest(point, layer);
        }

        function NearestFire(e){
          var point = turf.point([e.latlng.lng, e.latlng.lat]);
          var layer = _this.fire;
          Nearest(point, layer);
        }

        function Nearest(point, layer){
          // console.log(point);
          // console.log(layer);
          var stations = [];
          for (var i = 0; i < layer.length; ++i) {
            stations.push(turf.point(layer[i].geometry.coordinates));
          }
          stations = turf.featureCollection(stations);
          var nearestStation = turf.nearestPoint(point, stations);
          //if line already exists, remove it before adding new one
          if (_this.path != null) {
            _this.leaf.removeLayer(_this.path);
          }
          // fix distance and create tooltip
          var tooltip;
          if ( nearestStation.properties.distanceToPoint < 1.0) {
            tooltip = "Distance is " + (nearestStation.properties.distanceToPoint * 1000).toFixed(2) + " m";
          } else {
            tooltip = "Distance is " + nearestStation.properties.distanceToPoint.toFixed(2) + " km";
          }
          _this.path = leaflet
            .polyline(
              [
                [
                point.geometry.coordinates[1], 
                point.geometry.coordinates[0]
                ],
                [
                  nearestStation.geometry.coordinates[1],
                  nearestStation.geometry.coordinates[0]
                ]
              ],
              { color: "red" }
            )
            .bindTooltip(tooltip)
            .addTo(_this.leaf);
          // get name of station
          var name;
          for (i = 0; i < layer.length; i++) {
            if (
              nearestStation.geometry.coordinates[0] ==
                layer[i].geometry.coordinates[0] &&
              nearestStation.geometry.coordinates[1] ==
                layer[i].geometry.coordinates[1]
            ) {
              name = layer[i].properties.name;
              break;
            }
          }

          console.log(name);
          // TODO: idk, probably make a marker where the user clicked or something

        }

        function clustertoggle(){
          if (_this.cluster){
            // remove toggle conext menu item and re-add it with new text
            _this.leaf.contextmenu.removeItem(6);
            _this.leaf.contextmenu.insertItem({
              text:'Cluster icons toggle: false',
              callback: clustertoggle
            }, 6);
            _this.cluster = false;
          }else{
            // remove toggle conext menu item and re-add it with new text
            _this.leaf.contextmenu.removeItem(6);
            _this.leaf.contextmenu.insertItem({
              text:'Cluster icons toggle: true',
              callback: clustertoggle
            }, 6);
            _this.cluster = true;
          }
          console.log(_this.cluster);
          eventBus.$emit("ReloadEmerg");
        }


      //adds scale bar
      leaflet.control.scale().addTo(this.leaf);
      //adds layer control to the map
      var defaultTile = { OpenStreetMap: OSMtile, Satellite: satellite };
      leaflet.control.layers(defaultTile).addTo(this.leaf);

      // add community boundaries to map
      axios
        .get("Community Boundaries.geojson")
        .then(function(response) {
          _this.communityB = response.data.features;
          var communityLayer = leaflet.geoJson(_this.communityB);

          //bind popup to all markers
          communityLayer.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });

          _this.leaf.addLayer(communityLayer);
        })
        .catch(function(error) {
          console.log(error);
        });
      // initialize emergcluster
      _this.emergcluster = leaflet.markerClusterGroup();
      // add police stations to map
      axios
        .get("https://data.calgary.ca/resource/ap4r-bav3.geojson")
        .then(function(response) {
          _this.police = response.data.features;
          //custom police icon
          var policeMarker = leaflet.divIcon({
            className: "marker",
            iconSize: [32, 32]
          });
          _this.policeLayer = leaflet.geoJson(_this.police, {
            pointToLayer: function(feature, latlng) {
              return leaflet
                .marker(latlng, { icon: policeMarker })
            }
          });

          //bind popup to all markers
          _this.policeLayer.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });
          // add to map and cluster layer
          _this.emergcluster.addLayer(_this.policeLayer);
          _this.leaf.addLayer(_this.policeLayer);
        })
        .catch(function(error) {
          console.log(error);
        });

      // add fire stations to map
      axios
        .get("https://data.calgary.ca/resource/cqsb-2hhg.geojson")
        .then(function(response) {
          _this.fire = response.data.features;
          //custom fire station icon
          var fireMarker = leaflet.divIcon({
            className: "marker3",
            iconSize: [32, 32]
          });
          _this.fireLayer = leaflet.geoJson(_this.fire, {
            pointToLayer: function(feature, latlng) {
              return leaflet
                .marker(latlng, { icon: fireMarker })
            }
          });

          //bind popup to all markers
          _this.fireLayer.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });
          // add to map and cluster layer
          _this.emergcluster.addLayer(_this.fireLayer);
          _this.leaf.addLayer(_this.fireLayer);
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
          _this.hosplayer = leaflet.geoJson(_this.hospitals, {
            pointToLayer: function(feature, latlng) {
              return leaflet.marker(latlng, { icon: hospMarker });
            }
          });

          _this.hosplayer.eachLayer(function(layer) {
            layer.bindTooltip(layer.feature.properties.name);
          });
          // add to map and cluster layer
          _this.emergcluster.addLayer(_this.hosplayer);
          _this.leaf.addLayer(_this.hosplayer);
        })
        .catch(function(error) {
          console.log(error);
        });

      //onclick function when users click on school marker
      // function onClick(e) {
      //   var school = turf.point([e.latlng.lng, e.latlng.lat]);
      //   var hosp = [];
      //   for (var i = 0; i < _this.hospitals.length; ++i) {
      //     hosp.push(turf.point(_this.hospitals[i].geometry.coordinates));
      //   }
      //   hosp = turf.featureCollection(hosp);
      //   var nearesthospital = turf.nearestPoint(school, hosp);
      //   //if line already exists, remove it before adding new one
      //   if (_this.path != null) {
      //     _this.leaf.removeLayer(_this.path);
      //   }
      //   // fix distance and create tooltip
      //   var tooltip;
      //   if ( nearesthospital.properties.distanceToPoint < 1.0) {
      //     tooltip = "Distance is " + (nearesthospital.properties.distanceToPoint * 1000).toFixed(2) + " m";
      //   } else {
      //     tooltip = "Distance is " + nearesthospital.properties.distanceToPoint.toFixed(2) + " km";
      //   }

      //   _this.path = leaflet
      //     .polyline(
      //       [
      //         [e.latlng.lat, e.latlng.lng],
      //         [
      //           nearesthospital.geometry.coordinates[1],
      //           nearesthospital.geometry.coordinates[0]
      //         ]
      //       ],
      //       { color: "red" }
      //     )
      //     .bindTooltip(tooltip)
      //     .addTo(_this.leaf);
      //   // get name of hospital
      //   var name;
      //   for (i = 0; i < _this.hospitals.length; i++) {
      //     if (
      //       nearesthospital.geometry.coordinates[0] ==
      //         _this.hospitals[i].geometry.coordinates[0] &&
      //       nearesthospital.geometry.coordinates[1] ==
      //         _this.hospitals[i].geometry.coordinates[1]
      //     ) {
      //       name = _this.hospitals[i].properties.name;
      //       break;
      //     }
      //   }
      //   eventBus.$emit("foundHospital", {
      //     school: e.target.feature.properties.name,
      //     hospital: name
      //   });
      //   _this.leaf.fitBounds(_this.path.getBounds());
      // }
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
