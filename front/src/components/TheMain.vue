<script setup>
import { nextTick, ref, computed } from 'vue'
import { NCard, NCode, NH1, NTag, NButton, NIcon, NTabs, NTabPane } from 'naive-ui'
import { useImageStore } from '@/stores/useImageStore'
import UploadImageBlock from './UploadImageBlock.vue'
import ImagePane from './ImagePane.vue'
import { EyeOutline as EyeIcon, EyeOffOutline as EyeOffIcon } from '@vicons/ionicons5'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

const isNumberDisabled = ref(false)
const isDigitDisabled = ref(false)
const imageStore = useImageStore()

const numberDisplay = computed(() => {
    return isNumberDisabled.value ? 'none' : 'block'
})

const digitDisplay = computed(() => {
    return isDigitDisabled.value ? 'none' : 'block'
})

const composeToPercent = (value) => {
    return Math.round(value * 10000) / 100
}

const getTagState = (value) => {
    if (value > 0.9) return 'success'
    if (value > 0.8) return 'warning'
    return 'error'
}

// const fillRectangles = async () => {
//     await nextTick()
//
//     if (!Array.isArray(imageStore.result?.objects)) return
//     const img = document.querySelector('#img-result')
//     const imgWrapper = document.querySelector('.img-result-wrapper')
//     const bounding = img.getBoundingClientRect()
//     const width = bounding.width
//     const height = bounding.height
//     // const actualWidth = imageStore.actualImageWidth
//     // const actualHeight = imageStore.actualImageHeight
//     const actualWidth = 640
//     const actualHeight = 640
//     const coeffX = width / actualWidth
//     const coeffY = height / actualHeight
//
//     imageStore.result.objects.forEach((obj) => {
//         const newX = obj.x * coeffX
//         const newY = obj.y * coeffY
//         const newWidth = obj.width * coeffX
//         const newHeight = obj.height * coeffY
//
//         const left = `${newX - newWidth / 2}px`
//         const top = `${newY - newHeight / 2}px`
//
//         const rect = document.createElement('div')
//         rect.style.left = left
//         rect.style.top = top
//         rect.style.width = newWidth + 'px'
//         rect.style.height = newHeight + 'px'
//         rect.classList.add('image-rect')
//
//         const objClass = document.createElement('div')
//         objClass.classList.add('image-rect-class')
//         objClass.innerText = obj.class
//         rect.appendChild(objClass)
//
//         imgWrapper.insertAdjacentElement('beforeend', rect)
//     })
// }

const fillRectangles = async () => {
    await nextTick()
    // Здесь можно добавить код для рисования прямоугольников и меток
    if (!Array.isArray(imageStore.result?.objects)) return
    const canvas = document.getElementById('canvas-result')
    const ctx = canvas.getContext('2d')
    // Устанавливаем размеры canvas на 640x640
    const targetSize = 640

    const actualWidth = targetSize
    const actualHeight = targetSize
    const coeffX = targetSize / actualWidth
    const coeffY = targetSize / actualHeight

    imageStore.result.objects.forEach((obj, index) => {
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

const writeToClipboard = (text) => {
    navigator.clipboard.writeText(text)
}

let imgFile = null
const fillImage = async (file) => {
    const reader = new FileReader()
    imgFile = file

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
        }
    }

    reader.readAsDataURL(file.file)
}

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

            fillRectangles()
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

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image()
        img.src = src
        img.onload = () => {
            resolve(img)
        }

        img.onerror = reject
    })
}

function readFileAsync(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = reject
        reader.readAsDataURL(file)
    })
}

function canvasToBlob(canvas, type = 'image/png', quality = 1.0) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(
            (blob) => {
                if (blob) {
                    resolve(blob)
                } else {
                    reject(new Error('Canvas is empty'))
                }
            },
            type,
            quality
        )
    })
}

const sleep = async () => {
    await new Promise((resolve) => setTimeout(resolve, 3000))
}

const downloadAll = async () => {
    const jszip = imageStore.jszip
    const archive = imageStore.archive
    const zip = new JSZip()

    for (let i = 0; i < archive.length; i++) {
        const file = archive[i]
        const img = await jszip.file(file.name).async('blob')
        const canvas = document.createElement('canvas')

        const loadedFile = await readFileAsync(img)

        const imageTag = await loadImage(loadedFile)

        const ctx = canvas.getContext('2d')

        canvas.width = 640
        canvas.height = 640

        ctx.drawImage(imageTag, 0, 0, 640, 640)

        const imageObjects = imageStore.result.objects.filter((f) => {
            return f.filename === file.name
        })

        const targetSize = 640

        const actualWidth = targetSize
        const actualHeight = targetSize
        const coeffX = targetSize / actualWidth
        const coeffY = targetSize / actualHeight

        imageObjects.forEach((obj, index) => {
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

        const blob = await canvasToBlob(canvas, 'image/jpeg')
        zip.file(`${file.name}`, blob)
    }

    const zipBlob = await zip.generateAsync({ type: 'blob' })
    saveAs(zipBlob, `results_${Date.now()}.zip`)
}

const demoImage = async () => {
    const res = await fetch('/demo.jpg')
    const file = { file: await res.blob() }
    imageStore.startLoading()

    try {
        imageStore.setImage(file)
        fillImage(file)

        const formData = new FormData()
        formData.append('file', file.file)
        const response = await fetch('http://158.160.32.229/detect', {
            method: 'POST',
            body: formData
        })

        const data = await response.json()

        data.objects.forEach((obj) => (obj.visible = true))

        fillRectangles()
        imageStore.setResult(data)
    } finally {
        imageStore.stopLoading()
    }
}

function isImageFile(fileName) {
    const extension = fileName.split('.').pop().toLowerCase()
    return ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(extension)
}

const demoArchive = async () => {
    const res = await fetch('/demo.zip')
    const file = { file: await res.blob() }
    imageStore.startLoading()

    try {
        const new_zip = new JSZip()
        new_zip.loadAsync(file.file).then(function (zip) {
            imageStore.setZip(
                zip.filter(
                    (_, zipEntry) => isImageFile(zipEntry.name) && !zipEntry.name.includes('MACOSX')
                ),
                new_zip
            )
        })

        const formData = new FormData()
        formData.append('file', file.file)
        const response = await fetch('http://158.160.32.229/detect', {
            method: 'POST',
            body: formData
        })

        const data = await response.json()

        data.objects.forEach((obj) => (obj.visible = true))

        fillRectangles()
        imageStore.setResult(data)
    } finally {
        imageStore.stopLoading()
    }
}
</script>

<template>
    <div class="main-content" v-if="!imageStore.isArchive">
        <NCard class="main-content-image">
            <div class="img-result-wrapper">
                <canvas
                    v-show="imageStore.imageURL"
                    width="640"
                    height="640"
                    id="canvas-result"
                ></canvas>
                <div class="ocrloader" v-if="imageStore.isLoading && imageStore.imageURL">
                    <span></span>
                </div>
                <UploadImageBlock
                    v-show="!imageStore.imageURL"
                    @fill-image="fillImage"
                    @image-uploaded="fillRectangles"
                />
                <NButton
                    v-if="imageStore.hasResult"
                    @click="imageStore.reset"
                    type="error"
                    block
                    class="reset-btn"
                >
                    Загрузить другую фотографию
                </NButton>
            </div>
        </NCard>
        <NCard>
            <div
                v-if="!imageStore.hasResult"
                style="
                    display: flex;

                    align-items: center;
                    justify-content: center;

                    height: 100%;

                    font-size: 16px;
                "
            >
                <span> Ожидание загрузки фотографии или архива </span>
            </div>
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
                    v-for="(obj, index) in imageStore.result.objects"
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
    <div class="main-content" style="flex-direction: column" v-else>
        <NTabs type="card" animated placement="left">
            <NTabPane
                v-for="file in imageStore.archive"
                :name="file.name"
                :tab="file.name"
                :key="file.name"
            >
                <ImagePane :file="file" />
            </NTabPane>
        </NTabs>
        <NButton type="info" style="height: 40px" block @click="downloadAll">Скачать все</NButton>
        <NButton type="error" style="height: 40px" block @click="imageStore.reset">Сброс</NButton>
    </div>
    <!-- <NCard class="json-content" v-if="imageStore.hasResult"> -->
    <!--     <template #header> -->
    <!--         <div -->
    <!--             style=" -->
    <!--                 display: flex; -->
    <!---->
    <!--                 justify-content: space-between; -->
    <!--             " -->
    <!--         > -->
    <!--             <span> JSON </span> -->
    <!--             <NButton type="info" @click="writeToClipboard(imageStore.resultJSON)"> -->
    <!--                 Скопировать -->
    <!--             </NButton> -->
    <!--         </div> -->
    <!--     </template> -->
    <!--     <NCode :code="imageStore.resultJSON" language="json" /> -->
    <!-- </NCard> -->
    <div
        v-if="!imageStore.hasResult && !imageStore.isLoading"
        style="
            display: flex;

            gap: 10px;
        "
    >
        <NButton type="primary" style="width: calc(50% - 5px)" @click="demoImage">
            Демо изображение
        </NButton>
        <NButton type="primary" style="width: calc(50% - 5px)" @click="demoArchive">
            Демо архив
        </NButton>
    </div>
</template>

<style>
.main-content {
    display: flex;

    flex-wrap: nowrap;

    gap: 20px;

    margin-bottom: 20px;
}

.main-content-image {
    width: auto;
}

.main-content-result {
    display: flex;

    flex-direction: column;

    gap: 30px;

    width: 100%;
}

.main-info {
    display: flex;

    flex-wrap: wrap;

    gap: 10px;
}

.main-digit {
    margin-top: 20px;
}

.main-image {
    width: 640px;
    height: 640px;
}

@media (max-width: 980px) {
    .main-content {
        flex-direction: column;
    }

    .main-content-image {
        width: 100%;
    }

    .main-image {
        max-width: 100%;
        height: auto;
    }
}

.img-result-wrapper {
    position: relative;

    min-width: 640px;
    min-height: 640px;
}

.image-rect {
    position: absolute;

    box-sizing: border-box !important;

    display: v-bind('numberDisplay');

    border: 3px solid red;
}

.image-rect-class {
    position: absolute;
    right: -3px;
    bottom: 100%;

    box-sizing: border-box !important;

    display: v-bind('numberDisplay');

    padding: 3px 3px 5px;

    font-size: 14px;
    font-weight: bold;
    line-height: 1;
    color: white;

    background-color: red;
}

.img-control {
    display: flex;

    flex-direction: column;

    gap: 10px;

    margin-top: 20px;
}

.reset-btn {
    height: 60px;
    margin-top: 20px;
}

.json-content {
    margin-bottom: 20px;
}

.ocrloader {
    position: absolute;
    top: 0;
    left: 0;

    width: 640px;
    height: 640px;

    backface-visibility: hidden;

    span {
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1;

        width: 20px;
        height: 100%;

        background-color: rgb(99 226 183 / 54%);

        transform: translateX(0%);
        animation: move 1.5s ease-in-out;
        animation-iteration-count: infinite;
    }
}

@keyframes move {
    0%,
    100% {
        transform: translateX(0%);
    }

    50% {
        transform: translateX(1600%);
    }

    75% {
        transform: translateX(3100%);
    }
}

.main-deffect {
    padding: 10px;
}

.main-deffect:hover {
    background-color: rgb(255 255 255 / 5%);
}
</style>
