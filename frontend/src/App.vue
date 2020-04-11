<template>
 <v-app>
   <v-content class="pa-0">
    <toolbar/>
   </v-content>
 </v-app>
</template>

<script>
import toolbar from './components/toolbar';

export default {
  name: 'App',

  components: {
    toolbar,
  },

  data: () => ({
    //
  }),
};
</script>

<style scoped>
   * {
   overflow: hidden;
 }

</style>
