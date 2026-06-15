/**
 * ULTRON ATLAS 3D Scene Setup
 * Purpose: Initialize Three.js scene, lighting, and environmental setup
 * Features: Neon cyberpunk environment with dynamic lighting
 * Performance: Optimized for 60 FPS on modern browsers
 */

class ATLAS3DScene {
    constructor(containerElement) {
        this.container = containerElement;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.lights = {};
        this.environment = null;

        // Configuration
        this.config = {
            width: window.innerWidth,
            height: window.innerHeight,
            pixelRatio: window.devicePixelRatio,

            // Lighting
            ambientIntensity: 0.3,
            primaryLightColor: 0x00BFFF,      // Neon Blue
            secondaryLightColor: 0xFF6B35,    // Electric Orange
            accentLightColor: 0x00D9FF,       // Cyan

            // Colors
            backgroundColor: 0x0A0E27,        // Dark Navy

            // Performance
            antialias: true,
            shadowMapSize: 1024,
            maxPixelRatio: 2
        };

        this.init();
    }

    /**
     * Initialize the 3D scene
     */
    init() {
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupLighting();
        this.setupEnvironment();
        this.addEventListeners();
        this.animate();
    }

    /**
     * Setup Three.js scene
     */
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.config.backgroundColor);
        this.scene.fog = new THREE.Fog(
            this.config.backgroundColor,
            100,  // near
            500   // far
        );
    }

    /**
     * Setup camera with aspect ratio handling
     */
    setupCamera() {
        const aspect = this.config.width / this.config.height;
        const fov = 75;
        const near = 0.1;
        const far = 1000;

        this.camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
        this.camera.position.set(0, 0, 3);
        this.camera.lookAt(0, 0, 0);
    }

    /**
     * Setup WebGL renderer with optimization
     */
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            antialias: this.config.antialias,
            alpha: true,
            precision: 'highp',
            powerPreference: 'high-performance'
        });

        this.renderer.setSize(this.config.width, this.config.height);
        this.renderer.setPixelRatio(
            Math.min(this.config.pixelRatio, this.config.maxPixelRatio)
        );
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFShadowShadowMap;
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;

        this.container.appendChild(this.renderer.domElement);
    }

    /**
     * Setup lighting system with neon colors
     */
    setupLighting() {
        // Ambient light (soft overall illumination)
        const ambientLight = new THREE.AmbientLight(
            0xFFFFFF,
            this.config.ambientIntensity
        );
        this.scene.add(ambientLight);
        this.lights.ambient = ambientLight;

        // Primary neon blue light
        const primaryLight = new THREE.PointLight(
            this.config.primaryLightColor,
            1.5,
            100
        );
        primaryLight.position.set(5, 5, 5);
        primaryLight.castShadow = true;
        primaryLight.shadow.mapSize.width = this.config.shadowMapSize;
        primaryLight.shadow.mapSize.height = this.config.shadowMapSize;
        primaryLight.shadow.camera.near = 0.5;
        primaryLight.shadow.camera.far = 100;
        this.scene.add(primaryLight);
        this.lights.primary = primaryLight;

        // Secondary orange accent light
        const secondaryLight = new THREE.PointLight(
            this.config.secondaryLightColor,
            1.2,
            80
        );
        secondaryLight.position.set(-5, 5, -5);
        secondaryLight.castShadow = true;
        this.scene.add(secondaryLight);
        this.lights.secondary = secondaryLight;

        // Accent cyan light (from below for drama)
        const accentLight = new THREE.PointLight(
            this.config.accentLightColor,
            0.8,
            60
        );
        accentLight.position.set(0, -5, 3);
        this.scene.add(accentLight);
        this.lights.accent = accentLight;

        // Directional light for overall fill
        const dirLight = new THREE.DirectionalLight(0xFFFFFF, 0.4);
        dirLight.position.set(10, 10, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = this.config.shadowMapSize;
        dirLight.shadow.mapSize.height = this.config.shadowMapSize;
        dirLight.shadow.camera.left = -20;
        dirLight.shadow.camera.right = 20;
        dirLight.shadow.camera.top = 20;
        dirLight.shadow.camera.bottom = -20;
        this.scene.add(dirLight);
        this.lights.directional = dirLight;
    }

    /**
     * Setup environment (background elements, atmosphere)
     */
    setupEnvironment() {
        this.environment = {
            gridHelper: null,
            particles: null
        };

        // Add grid helper (optional visualization)
        const gridHelper = new THREE.GridHelper(100, 50, 0x00BFFF, 0x1A0033);
        gridHelper.position.y = -5;
        this.scene.add(gridHelper);
        this.environment.gridHelper = gridHelper;

        // Create particle system for ambient atmosphere
        this.createParticleSystem();
    }

    /**
     * Create ambient particle system for cyberpunk effect
     */
    createParticleSystem() {
        const particleCount = 500;
        const geometry = new THREE.BufferGeometry();

        const positions = new Float32Array(particleCount * 3);
        const velocities = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 100;      // X
            positions[i + 1] = (Math.random() - 0.5) * 100;  // Y
            positions[i + 2] = (Math.random() - 0.5) * 100;  // Z

            velocities[i] = (Math.random() - 0.5) * 0.1;
            velocities[i + 1] = (Math.random() - 0.5) * 0.1;
            velocities[i + 2] = (Math.random() - 0.5) * 0.1;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));

        const material = new THREE.PointsMaterial({
            color: 0x00BFFF,
            size: 0.1,
            sizeAttenuation: true,
            transparent: true,
            opacity: 0.6
        });

        const particles = new THREE.Points(geometry, material);
        this.scene.add(particles);
        this.environment.particles = particles;
    }

    /**
     * Animation loop
     */
    animate() {
        requestAnimationFrame(() => this.animate());

        // Update particles
        if (this.environment.particles) {
            this.updateParticles();
        }

        // Update lights with subtle animation
        this.animateLights();

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Update particle positions
     */
    updateParticles() {
        const positions = this.environment.particles.geometry.attributes.position.array;
        const velocities = this.environment.particles.geometry.attributes.velocity.array;

        for (let i = 0; i < positions.length; i += 3) {
            positions[i] += velocities[i];
            positions[i + 1] += velocities[i + 1];
            positions[i + 2] += velocities[i + 2];

            // Wrap around
            if (positions[i] > 50) positions[i] = -50;
            if (positions[i] < -50) positions[i] = 50;
            if (positions[i + 1] > 50) positions[i + 1] = -50;
            if (positions[i + 1] < -50) positions[i + 1] = 50;
            if (positions[i + 2] > 50) positions[i + 2] = -50;
            if (positions[i + 2] < -50) positions[i + 2] = 50;
        }

        this.environment.particles.geometry.attributes.position.needsUpdate = true;
    }

    /**
     * Animate lights for dynamic atmosphere
     */
    animateLights() {
        const time = Date.now() * 0.001;

        // Gentle oscillation of light intensities
        this.lights.primary.intensity = 1.5 + Math.sin(time * 0.5) * 0.3;
        this.lights.secondary.intensity = 1.2 + Math.cos(time * 0.4) * 0.2;

        // Subtle position changes
        this.lights.primary.position.x = 5 + Math.sin(time * 0.3) * 2;
        this.lights.secondary.position.z = -5 + Math.cos(time * 0.3) * 2;
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        this.config.width = window.innerWidth;
        this.config.height = window.innerHeight;

        this.camera.aspect = this.config.width / this.config.height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(this.config.width, this.config.height);
    }

    /**
     * Add event listeners
     */
    addEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
    }

    /**
     * Get scene object for adding elements
     */
    getScene() {
        return this.scene;
    }

    /**
     * Get camera object
     */
    getCamera() {
        return this.camera;
    }

    /**
     * Get renderer object
     */
    getRenderer() {
        return this.renderer;
    }

    /**
     * Dispose and clean up
     */
    dispose() {
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ATLAS3DScene;
}
