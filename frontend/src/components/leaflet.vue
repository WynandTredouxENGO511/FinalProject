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
import "leaflet-side-by-side"
import { load } from 'recaptcha-v3';
import "leaflet.heat";

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
      communityB: null,
      // sidebyside
      sbs: null,
      // recaptcha score
      // this should be checked before an incident can be reported
      captchaScore: 0,
      // Variables to store crime data for left/right queries
      crime_left: null,
      crime_right: null, 
      // Variables to store heatmaps for left/right queries
      heatmap_left: null,
      heatmap_right: null,
    };
  },

  mounted() {
  
    this.initMap();
    // clear path lines
    eventBus.$on("clear", () => {
      if (this.path != null) {
        this.leaf.removeLayer(this.path);
      }
    });
    // switch between clustered/unclustered
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
    // get captcha value
    eventBus.$on("getScore", () => {
      eventBus.$emit("setScore", this.captchaScore);
    });
    // return query responses from visualize()
    eventBus.$on("setVisData", data => {
      var side = data[0];
      var response = data[1];

      if (side=='left'){
        this.crime_left = response;
        this.updateHeatmaps('left', this.crime_left)
      }else{
        this.crime_right = response;
        this.updateHeatmaps('right', this.crime_right)
      }
    });
    eventBus.$on("clearheatmaps", () => {
      if (this.heatmap_left!=null){
         this.leaf.removeLayer(this.heatmap_left);
         this.heatmap_left = null;
      }

      if (this.heatmap_right!=null){
         this.leaf.removeLayer(this.heatmap_right);
         this.heatmap_right = null;
      }
    });

  },

  methods: {
    getCommunityCentre(name){
      var centroid = [];
      for (var i = 0; i<this.communityB.length; i++){
        if (this.communityB[i].properties.name == name){
          centroid = turf.centroid(this.communityB[i]);
          break;
        }
      }
      return centroid;
    },

    // draw heatmap
    updateHeatmaps(side, data){
      if (side == 'left' && this.heatmap_left!=null){
         this.leaf.removeLayer(this.heatmap_left);
         this.heatmap_left = null;
      }

      if (side == 'right' && this.heatmap_right!=null){
         this.leaf.removeLayer(this.heatmap_right);
         this.heatmap_right = null;
      }

      data = data.data.data;
      console.log(side);
      //console.log(data);
      // get a list of all communities with their centers
      var centroid = this.getCommunityCentre(data[0].community);
      var maxcount = 0;
      var communityCount = [{name: data[0].community,
                              count: 0,
                              centroid: centroid}]; // keep track of the crime per community [name count centroid]
      // sum up crime for each community
      for (var i=0; i<data.length; i++){
        var name = data[i].community;
        var count = data[i].count;
        // find if name exists in communityCount
        var index = null;
        for (var j=0; j<communityCount.length; j++){
          if (communityCount[j].name==name){
            index = j;
            break;
          }
        }
        // if no community by that name is found, add it to the array
        if (index == null){
          //find lat/long of community
          centroid = this.getCommunityCentre(name);      

          communityCount.push(
            {name: name,
            count: count,
            centroid: centroid}
          );
          // keep track of largest count
          if (count > maxcount){
            maxcount = count;
          }
        }else{
          communityCount[index].count += count;
          // keep track of largest count
          if (communityCount[index].count > maxcount){
            maxcount = communityCount[index].count;
          }
        }
      }
      //console.log(communityCount);
      //console.log(maxcount);
      // now that crime has been summed for all communities and their
      // centroids have been found, create array for heatmap
      var heat = new Array(communityCount.length);
      var counter = 0;
      for (i = 0; i<communityCount.length; i++){
        // set lat, long, intensity (where intensity = count/(max count))
        //console.log(i);
        var intensity = communityCount[i].count/maxcount;
        if (communityCount[i].centroid.length == 0){
            // skip
            continue;
        }
        heat[counter] = [communityCount[i].centroid.geometry.coordinates[1], communityCount[i].centroid.geometry.coordinates[0], intensity];
        counter += 1;
      }
      heat = heat.slice(0,counter);
      console.log('heat_done!')
      //console.log(heat);
      // now finally create heatmap
       var opacity = 0.5;
      if (side=='left'){
        this.heatmap_left = leaflet.heatLayer(heat, {
        radius: 50,
        minOpacity: opacity,
        // gradient : {0.3: '#5efffd', 0.5: '#6ba9fe', 0.8:'#a651ff', 1: '#f200fc'}
        });
        
        this.leaf.addLayer(this.heatmap_left);
      }else{
        this.heatmap_right = leaflet.heatLayer(heat, {
        radius: 50,
        minOpacity: opacity,
        gradient : {0.3: '#fbff66', 0.5: '#b6dc64', 0.8:'#55a664', 1: '#288165'}
        });
        this.leaf.addLayer(this.heatmap_right);
      }
    },


    //initializes leaflet map
    initMap() {
      // get reCaptcha score
      load('6LedK-oUAAAAALk-pVAf9sQd6eoR4lbmOjhdRHgL').then((recaptcha) => {
        recaptcha.execute().then((token) => {
            // verifying the user's response
            const path = 'http://localhost:5000/cap';
            const payload = {
              response: token,
            };
            //axios.post(path, payload);
            axios.post(path, payload).then(function(response){
              _this.captchaScore = response.data.score;
              console.log('reCaptcha score: '.concat(_this.captchaScore));
            })
            .catch(function (error){
              console.log(error);
            });
        })
      });

      

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
                text: 'Show Coordinates',
                callback: showCoordinates
            }, {
                text: 'Center Map Here',
                callback: centerMap
            }, {
                text: 'Report Incident Here',
                callback: ReportInc
            },{
                text: 'See Reports Here',
                callback: ReportGet
            }, '-', {
                text: 'Zoom in',
                icon: 'https://img.icons8.com/metro/26/000000/zoom-in.png',
                callback: zoomIn
            }, {
                text: 'Zoom out',
                icon: 'https://img.icons8.com/metro/26/000000/zoom-out.png',
                callback: zoomOut
            },{
              text:'Cluster Icons Toggle: false',
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

        function ReportGet(e){
          // check which community the coordinate is in
          var point = turf.point([e.latlng.lng, e.latlng.lat]);
          var communityName = '';
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
            console.log('get reports!')
            const path = 'http://localhost:5000/queryusers';
            // always submit left query
            axios.get(path, {
                params: {
                  community: communityName
                }
              })
              .then(function (response) {
                //console.log(response);
                var reviews = response.data.data;
                eventBus.$emit("openuserForm", [communityName, reviews]);
              })
              .catch(function (error) {
                console.log(error);
              });
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
            _this.leaf.contextmenu.removeItem(7);
            _this.leaf.contextmenu.insertItem({
              text:'Cluster Icons Toggle: false',
              callback: clustertoggle
            }, 7);
            _this.cluster = false;
          }else{
            // remove toggle conext menu item and re-add it with new text
            _this.leaf.contextmenu.removeItem(7);
            _this.leaf.contextmenu.insertItem({
              text:'Cluster Icons Toggle: true',
              callback: clustertoggle
            }, 7);
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
      //leaflet side-by-side
      _this.sbs = leaflet.control.sideBySide(_this.heatmap_left, _this.heatmap_right)
      //_this.sbs.addTo(this.leaf);

      // add community boundaries to map
      axios
        .get("Community Boundaries.geojson")
        .then(function(response) {
          _this.communityB = response.data.features;
          eventBus.$emit("setCommunities", _this.communityB);
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

        //add crime data to the map
        // axios
        // .get("Community Crime Statistics.geojson")
        // .then(function(response) {
        //   _this.crime = response;
        // })
        // .catch(function(error) {
        //   console.log(error);
        // });
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
