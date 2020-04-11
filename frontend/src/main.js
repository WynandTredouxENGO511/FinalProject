import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import vuetify from './plugins/vuetify';

Vue.config.productionTip = false
//constant variable eventbus
export const eventBus = new Vue();

new Vue({
  axios,
  vuetify,
  render: h => h(App)
}).$mount('#app')