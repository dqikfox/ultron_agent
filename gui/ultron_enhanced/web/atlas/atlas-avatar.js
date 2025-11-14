/**
 * ULTRON ATLAS 3D Avatar Model
 * Purpose: Create and manage the ATLAS AI robot 3D model
 * Features: Procedurally generated 3D robot with animations
 * Design: Neon blue/orange cyberpunk robot with glowing eyes and dynamic expressions
 */

class ATLASAvatar {
    constructor(scene) {
        this.scene = scene;
        this.model = null;
        this.parts = {};
        this.animations = {};
        this.state = {
            emotion: 'neutral',  // neutral, thinking, listening, speaking, happy, error
            isAnimating: false,
            eyeIntensity: 1.0
        };

        this.config = {
            // Colors
            primaryColor: 0x00BFFF,      // Neon Blue
            secondaryColor: 0xFF6B35,    // Electric Orange
            metalColor: 0x1A1A2E,        // Dark metal
            glowColor: 0x00BFFF,         // Glow blue

            // Scale
            scale: 1.5,

            // Materials
            metalMaterial: null,
            glowMaterial: null,
            eyeMaterial: null
        };

        this.init();
    }

    /**
     * Initialize the avatar
     */
    init() {
        this.createMaterials();
        this.createModel();
        this.positionModel();
    }

    /**
     * Create Three.js materials
     */
    createMaterials() {
        // Metallic material for body
        this.config.metalMaterial = new THREE.MeshStandardMaterial({
            color: this.config.metalColor,
            metalness: 0.8,
            roughness: 0.2,
            emissive: 0x00BFFF,
            emissiveIntensity: 0.1
        });

        // Secondary metallic (orange accents)
        this.orangeMaterial = new THREE.MeshStandardMaterial({
            color: this.config.secondaryColor,
            metalness: 0.7,
            roughness: 0.3,
            emissive: this.config.secondaryColor,
            emissiveIntensity: 0.2
        });

        // Glowing material for eyes
        this.config.eyeMaterial = new THREE.MeshBasicMaterial({
            color: this.config.glowColor,
            emissive: this.config.glowColor,
            emissiveIntensity: 2.0
        });

        // Glow material for accents
        this.config.glowMaterial = new THREE.MeshStandardMaterial({
            color: this.config.glowColor,
            metalness: 0.9,
            roughness: 0.1,
            emissive: this.config.glowColor,
            emissiveIntensity: 0.8
        });
    }

    /**
     * Create the main avatar model
     */
    createModel() {
        this.model = new THREE.Group();

        // Head (sphere)
        const headGeometry = new THREE.IcosahedronGeometry(0.5, 5);
        const head = new THREE.Mesh(headGeometry, this.config.metalMaterial);
        head.position.y = 0.8;
        head.castShadow = true;
        head.receiveShadow = true;
        this.model.add(head);
        this.parts.head = head;

        // Forehead ridge (orange accent)
        const ridgeGeometry = new THREE.BoxGeometry(0.6, 0.15, 0.5);
        const ridge = new THREE.Mesh(ridgeGeometry, this.orangeMaterial);
        ridge.position.set(0, 1.15, 0.35);
        ridge.castShadow = true;
        ridge.receiveShadow = true;
        this.model.add(ridge);
        this.parts.ridge = ridge;

        // Eyes (glowing spheres)
        this.createEyes();

        // Jaw (lower head section)
        const jawGeometry = new THREE.BoxGeometry(0.5, 0.25, 0.4);
        const jaw = new THREE.Mesh(jawGeometry, this.config.metalMaterial);
        jaw.position.y = 0.5;
        jaw.castShadow = true;
        jaw.receiveShadow = true;
        this.model.add(jaw);
        this.parts.jaw = jaw;

        // Neck (cylinder)
        const neckGeometry = new THREE.CylinderGeometry(0.25, 0.3, 0.3, 16);
        const neck = new THREE.Mesh(neckGeometry, this.config.metalMaterial);
        neck.position.y = 0.25;
        neck.castShadow = true;
        neck.receiveShadow = true;
        this.model.add(neck);
        this.parts.neck = neck;

        // Torso (main body)
        this.createTorso();

        // Shoulders
        this.createShoulders();

        // Arms (simple cylinders)
        this.createArms();

        // Scale the entire model
        this.model.scale.multiplyScalar(this.config.scale);

        // Add to scene
        this.scene.add(this.model);
    }

    /**
     * Create glowing eyes
     */
    createEyes() {
        const eyeRadius = 0.08;
        const eyeGeometry = new THREE.SphereGeometry(eyeRadius, 16, 16);

        // Left eye
        const leftEye = new THREE.Mesh(eyeGeometry, this.config.eyeMaterial);
        leftEye.position.set(-0.15, 0.95, 0.4);
        leftEye.castShadow = true;
        this.model.add(leftEye);
        this.parts.leftEye = leftEye;

        // Right eye
        const rightEye = new THREE.Mesh(eyeGeometry, this.config.eyeMaterial);
        rightEye.position.set(0.15, 0.95, 0.4);
        rightEye.castShadow = true;
        this.model.add(rightEye);
        this.parts.rightEye = rightEye;

        // Eye glow halos
        const haloGeometry = new THREE.IcosahedronGeometry(eyeRadius * 1.5, 4);

        const leftHalo = new THREE.Mesh(haloGeometry, this.config.glowMaterial);
        leftHalo.position.copy(leftEye.position);
        leftHalo.position.z -= 0.02;
        this.model.add(leftHalo);
        this.parts.leftHalo = leftHalo;

        const rightHalo = new THREE.Mesh(haloGeometry, this.config.glowMaterial);
        rightHalo.position.copy(rightEye.position);
        rightHalo.position.z -= 0.02;
        this.model.add(rightHalo);
        this.parts.rightHalo = rightHalo;
    }

    /**
     * Create torso
     */
    createTorso() {
        const torsoGeometry = new THREE.BoxGeometry(0.6, 1.0, 0.4);
        const torso = new THREE.Mesh(torsoGeometry, this.config.metalMaterial);
        torso.position.y = -0.2;
        torso.castShadow = true;
        torso.receiveShadow = true;
        this.model.add(torso);
        this.parts.torso = torso;

        // Chest plate (orange accent)
        const chestGeometry = new THREE.BoxGeometry(0.5, 0.6, 0.5);
        const chest = new THREE.Mesh(chestGeometry, this.orangeMaterial);
        chest.position.set(0, 0.1, 0.2);
        chest.castShadow = true;
        chest.receiveShadow = true;
        this.model.add(chest);
        this.parts.chest = chest;
    }

    /**
     * Create shoulders
     */
    createShoulders() {
        const shoulderGeometry = new THREE.SphereGeometry(0.2, 12, 12);

        // Left shoulder
        const leftShoulder = new THREE.Mesh(shoulderGeometry, this.config.metalMaterial);
        leftShoulder.position.set(-0.4, 0.2, 0);
        leftShoulder.castShadow = true;
        leftShoulder.receiveShadow = true;
        this.model.add(leftShoulder);
        this.parts.leftShoulder = leftShoulder;

        // Right shoulder
        const rightShoulder = new THREE.Mesh(shoulderGeometry, this.config.metalMaterial);
        rightShoulder.position.set(0.4, 0.2, 0);
        rightShoulder.castShadow = true;
        rightShoulder.receiveShadow = true;
        this.model.add(rightShoulder);
        this.parts.rightShoulder = rightShoulder;
    }

    /**
     * Create arms
     */
    createArms() {
        const armGeometry = new THREE.CylinderGeometry(0.1, 0.08, 0.7, 12);

        // Left arm
        const leftArm = new THREE.Mesh(armGeometry, this.config.metalMaterial);
        leftArm.position.set(-0.5, -0.1, 0);
        leftArm.rotation.z = 0.3;
        leftArm.castShadow = true;
        leftArm.receiveShadow = true;
        this.model.add(leftArm);
        this.parts.leftArm = leftArm;

        // Right arm
        const rightArm = new THREE.Mesh(armGeometry, this.config.metalMaterial);
        rightArm.position.set(0.5, -0.1, 0);
        rightArm.rotation.z = -0.3;
        rightArm.castShadow = true;
        rightArm.receiveShadow = true;
        this.model.add(rightArm);
        this.parts.rightArm = rightArm;

        // Hand indicators (orange glow)
        const handGeometry = new THREE.SphereGeometry(0.08, 12, 12);

        const leftHand = new THREE.Mesh(handGeometry, this.orangeMaterial);
        leftHand.position.set(-0.5, -0.6, 0);
        leftHand.castShadow = true;
        this.model.add(leftHand);
        this.parts.leftHand = leftHand;

        const rightHand = new THREE.Mesh(handGeometry, this.orangeMaterial);
        rightHand.position.set(0.5, -0.6, 0);
        rightHand.castShadow = true;
        this.model.add(rightHand);
        this.parts.rightHand = rightHand;
    }

    /**
     * Position model in scene
     */
    positionModel() {
        this.model.position.set(0, 0, 0);
        this.model.rotation.order = 'YXZ';
    }

    /**
     * Set emotional state with visual feedback
     */
    setEmotion(emotion) {
        this.state.emotion = emotion;

        switch (emotion) {
            case 'thinking':
                this.animateThinking();
                break;
            case 'listening':
                this.animateListening();
                break;
            case 'speaking':
                this.animateSpeaking();
                break;
            case 'happy':
                this.animateHappy();
                break;
            case 'error':
                this.animateError();
                break;
            case 'neutral':
            default:
                this.animateNeutral();
        }
    }

    /**
     * Animate thinking state (slow rotation, pulsing eyes)
     */
    animateThinking() {
        if (this.animations.thinking) clearInterval(this.animations.thinking);

        let time = 0;
        this.animations.thinking = setInterval(() => {
            time += 0.016;

            // Slow rotation
            this.model.rotation.y = Math.sin(time * 0.5) * 0.3;

            // Pulsing eye glow
            const eyePulse = 1.0 + Math.sin(time * 2) * 0.4;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.emissiveIntensity = eyePulse;
                this.parts.rightEye.material.emissiveIntensity = eyePulse;
            }
        }, 16);
    }

    /**
     * Animate listening state (tilt head, intense eyes)
     */
    animateListening() {
        if (this.animations.listening) clearInterval(this.animations.listening);

        let time = 0;
        this.animations.listening = setInterval(() => {
            time += 0.016;

            // Head tilt
            this.model.rotation.z = Math.sin(time * 1.5) * 0.15;

            // Intense glowing eyes
            const intensity = 2.0 + Math.sin(time * 3) * 0.5;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.emissiveIntensity = intensity;
                this.parts.rightEye.material.emissiveIntensity = intensity;
            }
        }, 16);
    }

    /**
     * Animate speaking state (jaw animation, rhythmic glow)
     */
    animateSpeaking() {
        if (this.animations.speaking) clearInterval(this.animations.speaking);

        let time = 0;
        this.animations.speaking = setInterval(() => {
            time += 0.016;

            // Jaw movement (scale Y)
            const jawScale = 1.0 + Math.sin(time * 4) * 0.3;
            if (this.parts.jaw) {
                this.parts.jaw.scale.y = jawScale;
            }

            // Breathing animation (vertical bob)
            this.model.position.y = Math.sin(time * 2) * 0.1;

            // Rhythmic eye glow matching speech
            const speechGlow = 1.5 + Math.sin(time * 3) * 0.6;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.emissiveIntensity = speechGlow;
                this.parts.rightEye.material.emissiveIntensity = speechGlow;
            }
        }, 16);
    }

    /**
     * Animate happy state (smile-like effect, energetic eyes)
     */
    animateHappy() {
        if (this.animations.happy) clearInterval(this.animations.happy);

        let time = 0;
        this.animations.happy = setInterval(() => {
            time += 0.016;

            // Bouncy movement
            this.model.position.y = Math.sin(time * 3) * 0.2;
            this.model.rotation.z = Math.sin(time * 2) * 0.2;

            // Bright eyes
            const brightness = 2.0 + Math.sin(time * 2) * 0.8;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.emissiveIntensity = brightness;
                this.parts.rightEye.material.emissiveIntensity = brightness;
            }
        }, 16);
    }

    /**
     * Animate error state (red flashing, shaking)
     */
    animateError() {
        if (this.animations.error) clearInterval(this.animations.error);

        let time = 0;
        this.animations.error = setInterval(() => {
            time += 0.016;

            // Shake effect
            this.model.position.x = Math.sin(time * 8) * 0.1;
            this.model.rotation.z = Math.sin(time * 10) * 0.05;

            // Red flashing eyes
            const flash = Math.sin(time * 5) > 0 ? 1 : 0;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.color.setHex(flash ? 0xFF0000 : 0x00BFFF);
                this.parts.rightEye.material.color.setHex(flash ? 0xFF0000 : 0x00BFFF);
                this.parts.leftEye.material.emissiveIntensity = 2.5;
                this.parts.rightEye.material.emissiveIntensity = 2.5;
            }
        }, 16);
    }

    /**
     * Animate neutral state (breathing, idle glow)
     */
    animateNeutral() {
        if (this.animations.neutral) clearInterval(this.animations.neutral);

        let time = 0;
        this.animations.neutral = setInterval(() => {
            time += 0.016;

            // Gentle breathing
            this.model.position.y = Math.sin(time * 1) * 0.05;

            // Steady eye glow
            const baseGlow = 1.5 + Math.sin(time * 1.5) * 0.3;
            if (this.parts.leftEye && this.parts.rightEye) {
                this.parts.leftEye.material.emissiveIntensity = baseGlow;
                this.parts.rightEye.material.emissiveIntensity = baseGlow;
            }
        }, 16);
    }

    /**
     * Look at a target position
     */
    lookAt(x, y, z) {
        const target = new THREE.Vector3(x, y, z);
        const direction = target.sub(this.model.position).normalize();

        // Calculate rotation to look at target
        const targetQuaternion = new THREE.Quaternion();
        targetQuaternion.setFromUnitVectorAndAxis(
            direction,
            new THREE.Vector3(0, 1, 0)
        );

        // Smooth interpolation (slerp)
        this.model.quaternion.slerp(targetQuaternion, 0.1);
    }

    /**
     * Point at a location
     */
    pointAt(x, y, z) {
        if (this.parts.rightArm) {
            this.parts.rightArm.lookAt(x, y, z);
        }
    }

    /**
     * Get the model group
     */
    getModel() {
        return this.model;
    }

    /**
     * Cleanup
     */
    dispose() {
        // Clear all animations
        Object.values(this.animations).forEach(anim => clearInterval(anim));

        // Dispose geometries and materials
        Object.values(this.parts).forEach(part => {
            if (part.geometry) part.geometry.dispose();
            if (part.material) part.material.dispose();
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ATLASAvatar;
}
