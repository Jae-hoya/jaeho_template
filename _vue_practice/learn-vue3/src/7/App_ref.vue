<template>
    <div>
            <p>{{ message }}</p>
            <button v-on:click="add_Messagge">add click!</button>
            <p>{{ message2 }}</p>
            <button v-on:click="add_Messagge2">add click!</button>
            <p>{{ message3 }}</p>
            <button v-on:click="add_Messagge3">add click!</button>
    </div>
</template>

<script>
import { reactive, ref } from 'vue';
export default {
    setup () {

        let message = reactive("hello vue!-reactive")  // 반응형으로 동작하지 않는다.
        let message2 = reactive({
            value: "hello vue3!-reactive" // 반응형으로 동작하기 위해서는 그 값을 넣어줘야 한다. / 하지만 애초에 ref를 제공하는 것이므로 이걸 쓴다.
        })

        let message3 = ref("hello vue3!-ref")

        
        const add_Messagge = () => {
            message = message + '!';
        }
        const add_Messagge2 = () => {
            message2.value = message2.value + '!';
        }       
        
        const add_Messagge3 = () => {
            message3.value = message3.value + '!';
        }
        
        console.log('message', message)
        console.log('message typeof', typeof message) // 아에 값이 스트링이다.

        console.log('message3', message3)
        console.log('message3 typeof', typeof message3.value) // 아에 값이 스트링이다.
        return {
            message,
            add_Messagge,
            message2,
            add_Messagge2,
            message3,
            add_Messagge3
        }
    }
}

</script>

<style lang="scss" scoped>

</style>

// reactive는 객체를 반응형으로 만들어준다. 
// ref는 기본값을을 반응형으로 만들어준다. 반응형 객체는 value의 참조 역할만 하는것이다.
