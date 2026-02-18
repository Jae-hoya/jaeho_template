<template>
    <div>
        <h2>보간법</h2>
        <p> {{ message }} </p>
        <p v-once> {{ message }} </p> 
        <button v-on:click="message = message + '!'"> !추가 </button>
        <hr>
        <h2>HTML</h2>
        <p>{{ rawHTML }}</p>
        <p v-html="rawHTML"></p>

        <h2>v-bind 속성 바인딩</h2>
        <div v-bind:title="dynamicTtile">마우스를 올려보세요</div>
        <input type="text" value="김재호" v-bind:disalbed='isInputDisabled' />
        <input v-bind="attrs" />

    </div>
</template>

<script>
import { ref } from 'vue'

export default {
    setup () {
        const message = ref('안녕하세요!')
        const rawHTML = ref('<strong>안녕하세요</strong>')
        const dynamicTtile = ref("안녕하세요!!!")
        const isInputDisabled = ref(true)
        const attrs = ref({
            type: 'password',
            value: '12345678',
            disabled: false
        })

        return {
            message,
            rawHTML,
            dynamicTtile,
            isInputDisabled,
            attrs
        }
    }
}
</script>

<style lang="scss" scoped>

</style>