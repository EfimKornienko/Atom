<script setup>
import { onMounted, ref, computed, nextTick, watchEffect } from 'vue'
import JSZip from 'jszip'
import { NCard, NH1, NTag, NButton, NIcon } from 'naive-ui'
import { EyeOutline as EyeIcon, EyeOffOutline as EyeOffIcon } from '@vicons/ionicons5'
import BaseLoader from './BaseLoader.vue'

import { useImageStore } from '../stores/useImageStore.js'

const props = defineProps({
    file: {
        type: null,
        required: true
    }
})

const imageStore = useImageStore()
const image = ref(null)

const fileResults = computed(() => {
    return imageStore.result.objects.filter((f) => {
        console.log(f.filename, props.file.name)
        return f.filename === props.file.name
    })
})

const fillRectangles = async () => {
    await nextTick()
    // Здесь можно добавить код для рисования прямоугольников и меток
    if (!Array.isArray(fileResults.value)) return
    const canvas = document.getElementById('canvas-result')
    const ctx = canvas.getContext('2d')
    // Устанавливаем размеры canvas на 640x640
    const targetSize = 640

    const actualWidth = targetSize
    const actualHeight = targetSize
    const coeffX = targetSize / actualWidth
    const coeffY = targetSize / actualHeight

    fileResults.value.forEach((obj, index) => {
        if (obj.visible) {
            const newX = obj.x * coeffX
            const newY = obj.y * coeffY
            const newWidth = obj.width * coeffX
            const newHeight = obj.height * coeffY
            const color = !obj.highlight ? 'red' : 'green'

            const left = newX - newWidth / 2
            const top = newY - newHeight / 2

            // Рисуем прямоугольник
            ctx.strokeStyle = color
            ctx.lineWidth = 3
            ctx.strokeRect(left, top, newWidth, newHeight)

            // Устанавливаем шрифт и измеряем текст
            ctx.font = 'bold 16px Arial'
            const padding = 4 // отступ вокруг текста
            const text = `#${index + 1} ${obj.class}`
            const textWidth = ctx.measureText(text).width
            const textHeight = 16 // предполагаемая высота текста

            // Рисуем фон для текста
            ctx.fillStyle = color
            ctx.fillRect(
                left - 3,
                top - textHeight - padding - 3,
                textWidth + 2 * padding,
                textHeight + 2 * padding
            )

            // Рисуем текст
            ctx.fillStyle = 'white'
            ctx.fillText(text, left + padding - 3, top - padding - 3)
        }
    })
}

let imgFile = null
const refillImage = () => {
    const file = imgFile
    const reader = new FileReader()

    reader.onload = function (e) {
        const img = new Image()
        img.src = e.target.result

        img.onload = function () {
            const canvas = document.getElementById('canvas-result')
            const ctx = canvas.getContext('2d')

            // Устанавливаем размеры canvas на 640x640
            const targetSize = 640
            canvas.width = targetSize
            canvas.height = targetSize

            // Рисуем изображение на canvas с изменением размеров до 640x640
            ctx.drawImage(img, 0, 0, targetSize, targetSize)

            if (!imageStore.isLoading) {
                fillRectangles()
            }
        }
    }

    reader.readAsDataURL(file.file)
}

const classNames = {
    adj: 'прилегающие дефекты',
    int: 'дефекты целостности',
    geo: 'дефекты геометрии',
    pro: 'дефекты постобработки',
    non: 'дефекты невыполнения'
}
const getClassName = (className) => {
    return classNames[className]
}

const changeVisible = (obj) => {
    obj.visible = !obj.visible

    refillImage()
}

const highlightObj = (obj) => {
    obj.highlight = true

    refillImage()
}

const unhighlightObj = (obj) => {
    obj.highlight = false

    refillImage()
}

const downloadImg = () => {
    const canvas = document.getElementById('canvas-result')
    const url = canvas.toDataURL('image/png')

    // Создаем ссылку для скачивания
    const a = document.createElement('a')
    a.href = url
    a.download = `${Date.now()}.jpg` // Имя файла для скачивания

    // Добавляем ссылку в документ и эмулируем клик по ней
    document.body.appendChild(a)
    a.click()

    // Удаляем ссылку из документа
    document.body.removeChild(a)
}

const composeToPercent = (value) => {
    return Math.round(value * 10000) / 100
}

const getTagState = (value) => {
    if (value > 0.9) return 'success'
    if (value > 0.8) return 'warning'
    return 'error'
}

onMounted(async () => {
    const img = await imageStore.jszip.file(props.file.name).async('blob')
    image.value = { file: img }
    imgFile = image.value

    refillImage()
})

watchEffect(() => {
    if (!imageStore.isLoading && imgFile) {
        refillImage()
    }
})
</script>

<template>
    <div class="main-content">
        <NCard class="main-content-image">
            <div class="img-result-wrapper">
                <div class="ocrloader" v-if="imageStore.isLoading">
                    <span></span>
                </div>

                <canvas width="640" height="640" id="canvas-result"></canvas>
            </div>
        </NCard>
        <NCard>
            <BaseLoader v-if="imageStore.isLoading" />
            <div class="main-content-result" v-if="imageStore.hasResult">
                <div
                    style="
                        display: flex;

                        justify-content: flex-end;
                    "
                >
                    <NButton type="info" @click="downloadImg"> Скачать изображение </NButton>
                </div>
                <div
                    class="main-deffect"
                    v-for="(obj, index) in fileResults"
                    :key="index"
                    @mouseover="highlightObj(obj)"
                    @mouseleave="unhighlightObj(obj)"
                >
                    <div
                        style="
                            display: flex;

                            justify-content: space-between;
                        "
                    >
                        <NH1>Деффект #{{ index + 1 }}</NH1>
                        <NButton type="primary" @click="changeVisible(obj)">
                            <NIcon size="18" :depth="1" color="#000">
                                <EyeOffIcon v-if="obj.visible" />
                                <EyeIcon v-else />
                            </NIcon>
                        </NButton>
                    </div>
                    <div class="main-info">
                        <NTag type="info" :bordered="false">
                            Координаты: ({{ obj.x }}, {{ obj.y }})
                        </NTag>
                        <NTag type="info" :bordered="false">
                            Размер: {{ obj.width }}x{{ obj.height }}
                        </NTag>
                        <NTag type="primary" :bordered="false">
                            Класс: {{ getClassName(obj.class) }}({{ obj.class }})
                        </NTag>
                        <NTag :type="getTagState(obj.confidence)" :bordered="false">
                            Уверенность: {{ composeToPercent(obj.confidence) }}%
                        </NTag>
                    </div>
                </div>
            </div>
        </NCard>
    </div>
</template>
