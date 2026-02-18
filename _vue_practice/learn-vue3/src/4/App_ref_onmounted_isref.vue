<template>
    <div>
        <h2> 반응형 메시지 </h2>
        <p> {{ reactiveMessage }}</p>
        <button v-on:click="addReactiveMessage">Add Message</button>
        <h2> 일반 메시지 </h2>
        <p> {{ normalMesssage }}</p>
        <button v-on:click="addnormalMessage">Add Message</button>
    </div>
</template>

<script>
import { ref, isRef, onMounted, onBeforeMount } from 'vue';

export default {
    setup () {
        console.log('setup()')

        const reactiveMessage = ref("Hello Reactive Message");
        const addReactiveMessage = () => {
            reactiveMessage.value = reactiveMessage.value + '!'
        }
        
        // isRef 반응형 메시지인지 확인
        // console.log('reactiveMessage', isRef(reactiveMessage)) 

        // const normalMesssage = "Hello Normal Message";
        let normalMesssage = "Hello Normal Message";
        const addnormalMessage = normalMesssage + '!'
        //  console.log('normalMesssage', isRef(normalMesssage)) 

        // 리사이클훅
        onMounted(()=>{
            console.log('onMounted')
        });
        onBeforeMount(()=>{
            console.log('onBeforeMount')
        });

        return {
            reactiveMessage,
            normalMesssage,
            addReactiveMessage,
            addnormalMessage
        }
    }
}
</script>

<style lang="scss" scoped>

</style>