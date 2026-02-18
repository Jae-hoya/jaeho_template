<template>
    <div>
        <h2>보간법</h2>
        <p>{{ message }}</p>
        <p v-once>{{ message }}</p>
        <button v-on:click="message = message + '!'"> click! </button>
    </div>
</template>

<script>
import { ref } from 'vue';

export default {
    setup () {
        const message = ref("안녕하세요!");

        return {
            message
        }
    }
}
</script>

<style lang="scss" scoped>

</style>
