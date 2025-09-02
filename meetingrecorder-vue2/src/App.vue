<template>
  <div id="app">
    <MeetingRecorder />
  </div>
</template>

<script>
import MeetingRecorder from './components/MeetingRecorder.vue';

export default {
  name: 'App',
  components: {
    MeetingRecorder
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
