import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# Streamlit
# =========================================================

st.set_page_config(
    page_title="3D 세계 여행 지도",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 세계 여행 안전 지도")

st.caption(
    "지구본을 드래그해서 회전하고 "
    "마우스 휠로 확대·축소해보세요."
)


# =========================================================
# Three.js Globe
# =========================================================

globe_html = r"""
<div id="globe-container">
    <div id="loading-text">
        지구본을 불러오는 중...
    </div>
</div>


<style>

html,
body {
    margin: 0;
    padding: 0;

    overflow: hidden;

    background: transparent;
}


#globe-container {
    position: relative;

    width: 100%;
    height: 820px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 50% 48%,
            rgba(35, 165, 230, 0.13) 0%,
            rgba(35, 165, 230, 0.04) 40%,
            rgba(255,255,255,0) 70%
        );
}


#loading-text {
    position: absolute;

    left: 50%;
    top: 50%;

    transform:
        translate(-50%, -50%);

    font-family:
        Arial,
        sans-serif;

    font-size: 14px;

    color:
        rgba(50,80,100,0.65);
}


canvas {
    display: block;
}

</style>


<script type="importmap">
{
    "imports": {

        "three":
        "https://cdn.jsdelivr.net/npm/three@0.179.1/build/three.module.js",

        "three/addons/":
        "https://cdn.jsdelivr.net/npm/three@0.179.1/examples/jsm/"
    }
}
</script>


<script type="module">

import * as THREE from "three";

import {
    OrbitControls
} from "three/addons/controls/OrbitControls.js";


// =========================================================
// 1. 기본 Scene
// =========================================================

const container =
    document.getElementById(
        "globe-container"
    );


const loadingText =
    document.getElementById(
        "loading-text"
    );


const scene =
    new THREE.Scene();


// =========================================================
// 2. Camera
// =========================================================

const camera =
    new THREE.PerspectiveCamera(

        38,

        container.clientWidth
        /
        container.clientHeight,

        0.01,

        100
    );


camera.position.set(
    0,
    0.05,
    3.35
);


// =========================================================
// 3. Renderer
// =========================================================

const renderer =
    new THREE.WebGLRenderer({

        antialias: true,

        alpha: true
    });


renderer.setPixelRatio(

    Math.min(
        window.devicePixelRatio,
        2
    )

);


renderer.setSize(

    container.clientWidth,

    container.clientHeight

);


renderer.outputColorSpace =
    THREE.SRGBColorSpace;


renderer.toneMapping =
    THREE.ACESFilmicToneMapping;


renderer.toneMappingExposure =
    1.12;


container.appendChild(
    renderer.domElement
);


// =========================================================
// 4. Controls
// =========================================================

const controls =
    new OrbitControls(

        camera,

        renderer.domElement
    );


controls.enableDamping = true;

controls.dampingFactor =
    0.055;


controls.rotateSpeed =
    0.72;


controls.zoomSpeed =
    0.85;


controls.enablePan =
    false;


controls.minDistance =
    2.0;


controls.maxDistance =
    5.5;


// =========================================================
// 5. 전체 지구 그룹
//
// 지구 / 구름 / 비행기가
// 전부 이 안에 들어감
// =========================================================

const world =
    new THREE.Group();


scene.add(
    world
);


// =========================================================
// 6. Texture Loader
// =========================================================

const textureLoader =
    new THREE.TextureLoader();


// =========================================================
// 7. 실제 지구 Texture
// =========================================================

// 실제 육지 + 바다 컬러
const earthColorTexture =
    textureLoader.load(

        "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg"

    );

earthColorTexture.colorSpace =
    THREE.SRGBColorSpace;


// 지표면 굴곡
const earthNormalTexture =
    textureLoader.load(

        "https://threejs.org/examples/textures/planets/earth_normal_2048.jpg"

    );


// 바다 반사 영역
const earthSpecularTexture =
    textureLoader.load(

        "https://threejs.org/examples/textures/planets/earth_specular_2048.jpg"

    );


// 실제 구름
const cloudTexture =
    textureLoader.load(

        "https://threejs.org/examples/textures/planets/earth_clouds_1024.png"

    );

cloudTexture.colorSpace =
    THREE.SRGBColorSpace;


// =========================================================
// 8. 🌍 지구 Sphere
// =========================================================

const EARTH_RADIUS =
    1;


const earthGeometry =
    new THREE.SphereGeometry(

        EARTH_RADIUS,

        128,

        128
    );


const earthMaterial =
    new THREE.MeshPhongMaterial({

        map:
            earthColorTexture,

        normalMap:
            earthNormalTexture,

        normalScale:
            new THREE.Vector2(
                0.35,
                0.35
            ),

        specularMap:
            earthSpecularTexture,

        specular:
            new THREE.Color(
                0x8bc9dd
            ),

        shininess:
            22
    });


const earth =
    new THREE.Mesh(

        earthGeometry,

        earthMaterial
    );


world.add(
    earth
);


// =========================================================
// 9. ☁️ 실제 구름 Sphere
//
// 지구보다 아주 조금 크게 만들어
// 지표면 위에 떠 있는 느낌
// =========================================================

const cloudGeometry =
    new THREE.SphereGeometry(

        1.008,

        128,

        128
    );


const cloudMaterial =
    new THREE.MeshPhongMaterial({

        map:
            cloudTexture,

        transparent:
            true,

        opacity:
            0.72,

        depthWrite:
            false,

        side:
            THREE.DoubleSide
    });


const clouds =
    new THREE.Mesh(

        cloudGeometry,

        cloudMaterial
    );


world.add(
    clouds
);


// =========================================================
// 10. ✨ 대기권
// =========================================================

const atmosphereGeometry =
    new THREE.SphereGeometry(

        1.025,

        128,

        128
    );


const atmosphereMaterial =
    new THREE.MeshBasicMaterial({

        color:
            0x66ccff,

        transparent:
            true,

        opacity:
            0.045,

        side:
            THREE.BackSide,

        depthWrite:
            false
    });


const atmosphere =
    new THREE.Mesh(

        atmosphereGeometry,

        atmosphereMaterial
    );


world.add(
    atmosphere
);


// =========================================================
// 11. 바깥쪽 Glow
// =========================================================

const outerGlowGeometry =
    new THREE.SphereGeometry(

        1.05,

        128,

        128
    );


const outerGlowMaterial =
    new THREE.MeshBasicMaterial({

        color:
            0x83ddff,

        transparent:
            true,

        opacity:
            0.018,

        side:
            THREE.BackSide,

        depthWrite:
            false
    });


const outerGlow =
    new THREE.Mesh(

        outerGlowGeometry,

        outerGlowMaterial
    );


world.add(
    outerGlow
);


// =========================================================
// 12. ☀️ Lighting
// =========================================================

// 전체 암부가 너무 검지 않도록
const ambientLight =
    new THREE.AmbientLight(

        0xbfe9ff,

        0.75
    );


scene.add(
    ambientLight
);


// 메인 태양
const sunLight =
    new THREE.DirectionalLight(

        0xfff6e5,

        3.2
    );


sunLight.position.set(
    -4,
    3,
    5
);


scene.add(
    sunLight
);


// 반대쪽 약한 푸른빛
const fillLight =
    new THREE.DirectionalLight(

        0x5dbce9,

        0.45
    );


fillLight.position.set(
    4,
    -2,
    -4
);


scene.add(
    fillLight
);


// 위쪽 약한 빛
const topLight =
    new THREE.DirectionalLight(

        0xd8f3ff,

        0.35
    );


topLight.position.set(
    0,
    5,
    0
);


scene.add(
    topLight
);


// =========================================================
// 13. 좌표 변환
//
// lat / lon → 3D Vector
// =========================================================

function latLonToVector3(
    lat,
    lon,
    radius = 1
) {

    const phi =
        THREE.MathUtils.degToRad(
            90 - lat
        );


    const theta =
        THREE.MathUtils.degToRad(
            lon + 180
        );


    const x =

        -radius

        *

        Math.sin(phi)

        *

        Math.cos(theta);


    const y =

        radius

        *

        Math.cos(phi);


    const z =

        radius

        *

        Math.sin(phi)

        *

        Math.sin(theta);


    return new THREE.Vector3(
        x,
        y,
        z
    );
}


// =========================================================
// 14. 서울 / 취리히
// =========================================================

const SEOUL = {

    lat:
        37.5665,

    lon:
        126.9780
};


const ZURICH = {

    lat:
        47.3769,

    lon:
        8.5417
};


// =========================================================
// 15. Great Circle
// =========================================================

const startDirection =
    latLonToVector3(

        SEOUL.lat,

        SEOUL.lon,

        1
    ).normalize();


const endDirection =
    latLonToVector3(

        ZURICH.lat,

        ZURICH.lon,

        1
    ).normalize();


function sphericalInterpolate(
    start,
    end,
    t
) {

    const a =
        start.clone().normalize();


    const b =
        end.clone().normalize();


    let dot =
        a.dot(b);


    dot =
        THREE.MathUtils.clamp(
            dot,
            -1,
            1
        );


    const angle =
        Math.acos(
            dot
        );


    if (
        angle < 0.00001
    ) {

        return a;
    }


    const sinAngle =
        Math.sin(
            angle
        );


    const scaleA =
        Math.sin(
            (1 - t) * angle
        )
        /
        sinAngle;


    const scaleB =
        Math.sin(
            t * angle
        )
        /
        sinAngle;


    return a
        .multiplyScalar(scaleA)
        .add(
            b.multiplyScalar(scaleB)
        )
        .normalize();
}


// =========================================================
// 16. 비행 위치 계산
//
// 경로선은 화면에 표시하지 않음
// =========================================================

const flightPoints =
    [];


const FLIGHT_STEPS =
    700;


for (
    let i = 0;
    i <= FLIGHT_STEPS;
    i++
) {

    const t =
        i
        /
        FLIGHT_STEPS;


    const direction =
        sphericalInterpolate(

            startDirection,

            endDirection,

            t
        );


    // 지표면 바로 위에서 비행
    const altitude =

        1.035

        +

        Math.sin(
            Math.PI * t
        )

        *

        0.020;


    direction.multiplyScalar(
        altitude
    );


    flightPoints.push(
        direction
    );
}


// =========================================================
// 17. ✈️ 3D 비행기
// =========================================================

const airplane =
    new THREE.Group();


// =========================================================
// 비행기 재질
// =========================================================

const planeWhite =
    new THREE.MeshStandardMaterial({

        color:
            0xf7f8f8,

        roughness:
            0.36,

        metalness:
            0.25
    });


const planeDark =
    new THREE.MeshStandardMaterial({

        color:
            0x1f6f93,

        roughness:
            0.38,

        metalness:
            0.15
    });


// =========================================================
// 동체
//
// 비행기 기수 방향은 +X
// =========================================================

const fuselageGeometry =
    new THREE.CapsuleGeometry(

        0.018,

        0.125,

        8,

        18
    );


const fuselage =
    new THREE.Mesh(

        fuselageGeometry,

        planeWhite
    );


// Capsule 기본축 Y → X축으로
fuselage.rotation.z =
    Math.PI / 2;


airplane.add(
    fuselage
);


// =========================================================
// 비행기 Nose
// =========================================================

const nose =
    new THREE.Mesh(

        new THREE.ConeGeometry(

            0.018,

            0.055,

            18
        ),

        planeWhite
    );


nose.rotation.z =
    -Math.PI / 2;


nose.position.x =
    0.091;


airplane.add(
    nose
);


// =========================================================
// Main Wings
// =========================================================

const wings =
    new THREE.Mesh(

        new THREE.BoxGeometry(

            0.052,

            0.006,

            0.175
        ),

        planeWhite
    );


wings.position.x =
    -0.005;


airplane.add(
    wings
);


// =========================================================
// Rear Wings
// =========================================================

const tailWing =
    new THREE.Mesh(

        new THREE.BoxGeometry(

            0.032,

            0.005,

            0.075
        ),

        planeDark
    );


tailWing.position.x =
    -0.065;


airplane.add(
    tailWing
);


// =========================================================
// Vertical Tail
// =========================================================

const tail =
    new THREE.Mesh(

        new THREE.BoxGeometry(

            0.032,

            0.052,

            0.006
        ),

        planeDark
    );


tail.position.set(

    -0.062,

    0.028,

    0
);


airplane.add(
    tail
);


// 비행기 크기
airplane.scale.setScalar(
    0.72
);


world.add(
    airplane
);


// =========================================================
// 18. 📍 서울 / 취리히 점
// =========================================================

function createMarker(
    lat,
    lon
) {

    const marker =
        new THREE.Mesh(

            new THREE.SphereGeometry(

                0.009,

                16,

                16
            ),

            new THREE.MeshBasicMaterial({

                color:
                    0xffffff
            })
        );


    marker.position.copy(

        latLonToVector3(

            lat,

            lon,

            1.012
        )

    );


    world.add(
        marker
    );
}


createMarker(

    SEOUL.lat,

    SEOUL.lon
);


createMarker(

    ZURICH.lat,

    ZURICH.lon
);


// =========================================================
// 19. 초기 방향
// =========================================================

world.rotation.y =
    -0.50;


world.rotation.x =
    0.08;


// =========================================================
// 20. 비행기 방향 함수
//
// ⭐ 이번 수정 핵심
//
// lookAt() 사용하지 않음.
//
// local X = 비행방향
// local Y = 지구 바깥쪽
// local Z = 날개 방향
// =========================================================

function orientAirplane(
    plane,
    currentPoint,
    nextPoint
) {

    // -----------------------------------------------------
    // 진행 방향
    // -----------------------------------------------------

    const forward =
        nextPoint
        .clone()
        .sub(
            currentPoint
        )
        .normalize();


    // -----------------------------------------------------
    // 지구 중심에서 바깥 방향
    //
    // 이것이 비행기의 "위"
    // -----------------------------------------------------

    const radialUp =
        currentPoint
        .clone()
        .normalize();


    // -----------------------------------------------------
    // 오른쪽 방향
    // -----------------------------------------------------

    const right =
        forward
        .clone()
        .cross(
            radialUp
        )
        .normalize();


    // -----------------------------------------------------
    // 실제 up을 다시 직교화
    // -----------------------------------------------------

    const correctedUp =
        right
        .clone()
        .cross(
            forward
        )
        .normalize();


    // -----------------------------------------------------
    // X축 = forward
    // Y축 = up
    // Z축 = right
    // -----------------------------------------------------

    const rotationMatrix =
        new THREE.Matrix4();


    rotationMatrix.makeBasis(

        forward,

        correctedUp,

        right
    );


    plane.quaternion.setFromRotationMatrix(
        rotationMatrix
    );

    // 비행기 모델의 좌우 기울기 보정
    plane.rotateX(
    THREE.MathUtils.degToRad(-45)
    );
}


// =========================================================
// 21. 애니메이션
// =========================================================

let flightProgress =
    0;


const FLIGHT_SPEED =
    0.00029;


let waiting =
    false;


let waitUntil =
    0;


// =========================================================
// Render loop
// =========================================================

function animate(time) {

    requestAnimationFrame(
        animate
    );


    controls.update();


    // -----------------------------------------------------
    // ☁️ 구름이 실제 지구보다 조금 빠르게 회전
    // -----------------------------------------------------

    clouds.rotation.y +=
        0.000035;


    // -----------------------------------------------------
    // 비행
    // -----------------------------------------------------

    if (
        waiting
    ) {

        if (
            time >= waitUntil
        ) {

            waiting =
                false;


            flightProgress =
                0;
        }

    }

    else {

        flightProgress +=
            FLIGHT_SPEED;


        if (
            flightProgress >= 1
        ) {

            flightProgress =
                1;


            waiting =
                true;


            waitUntil =
                time + 1400;
        }
    }


    // -----------------------------------------------------
    // 현재 위치
    // -----------------------------------------------------

    const floatIndex =

        flightProgress

        *

        (flightPoints.length - 1);


    const index =
        Math.floor(
            floatIndex
        );


    const nextIndex =
        Math.min(

            index + 1,

            flightPoints.length - 1
        );


    const fraction =

        floatIndex

        -

        index;


    const currentPoint =

        flightPoints[index]

        .clone()

        .lerp(

            flightPoints[nextIndex],

            fraction

        );


    airplane.position.copy(
        currentPoint
    );


    // -----------------------------------------------------
    // 기수가 향할 다음 위치
    // -----------------------------------------------------

    const lookIndex =
        Math.min(

            index + 5,

            flightPoints.length - 1
        );


    const lookPoint =
        flightPoints[
            lookIndex
        ];


    // =====================================================
    // ⭐ 비행기 방향 수정
    // =====================================================

    orientAirplane(

        airplane,

        currentPoint,

        lookPoint
    );


    renderer.render(

        scene,

        camera
    );
}


// =========================================================
// Texture가 하나라도 로드되기 시작하면
// 로딩 문구 제거
// =========================================================

earthColorTexture.onUpdate =
    () => {

        if (
            loadingText
        ) {

            loadingText.style.display =
                "none";
        }
    };


setTimeout(
    () => {

        if (
            loadingText
        ) {

            loadingText.style.display =
                "none";
        }

    },
    2500
);


animate(0);


// =========================================================
// Resize
// =========================================================

window.addEventListener(

    "resize",

    () => {

        const width =
            container.clientWidth;


        const height =
            container.clientHeight;


        camera.aspect =

            width
            /
            height;


        camera.updateProjectionMatrix();


        renderer.setSize(

            width,

            height
        );
    }
);

</script>
"""


# =========================================================
# Streamlit 출력
# =========================================================

components.html(
    globe_html,
    height=840,
    scrolling=False,
)