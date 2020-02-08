import Vue from 'vue';
import App from './App.vue';
import vuetify from './plugins/vuetify';
import Home from './components/Home.vue';

Vue.config.productionTip = false;
Vue.component('home', Home);

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app');
