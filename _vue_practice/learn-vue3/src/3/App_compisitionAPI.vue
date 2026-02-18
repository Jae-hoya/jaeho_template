// {{  }} 는 반응형 상태.
// setup함수 안에, const, onMounted등이 모아져 있다. data, method...등을 선언하는 대신, ref onMounted를 사용하여 Vue 컴포넌트를 작성할 수 있는 api세트.
<template>
  <div>
    <button @click="increment">Counter: {{ counter }}</button>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';

export default {
  setup () {
    const counter = ref(0)
    const increment = () => counter.value++;

    onMounted(() => {
      console.log("컴포넌트가 마운트 되었습니다.")
    });

    return {
      counter,
      increment
    }
  }
}
</script>

<style lang="scss" scoped>

</style>