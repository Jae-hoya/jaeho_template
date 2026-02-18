<template>
  <div>
    <button v-on:click="increment">Counter: {{ counter }}</button>
  </div>
</template>

<script>
export default {
  data () {
    return {
      counter: 0
    };
  },
  methods: {
    increment() {
      this.counter++;
    }
  },
  // 마운티드 메서드
  mounted() {
    console.log("컴포넌트가 마운트 되었씁니다.")
  }
};
</script>

<style lang="scss" scoped>

</style>