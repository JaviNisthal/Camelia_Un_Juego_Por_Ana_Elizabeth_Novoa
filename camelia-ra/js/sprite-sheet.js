/* Anima una lámina de fotogramas (una fila o cuadrícula) sobre un a-plane
   moviendo el desplazamiento UV de la textura. Más fiable que un GIF,
   que WebGL no anima. */
AFRAME.registerComponent('sprite-sheet', {
  schema: {
    frames: { type: 'int', default: 8 },
    columns: { type: 'int', default: 8 },
    rows: { type: 'int', default: 1 },
    fps: { type: 'number', default: 10 },
    playing: { type: 'boolean', default: true }
  },

  init: function () {
    this.elapsed = 0;
    this.frame = 0;
    this.texture = null;
    this.onTexture = this.onTexture.bind(this);
    this.el.addEventListener('materialtextureloaded', this.onTexture);
  },

  update: function () {
    if (this.texture) this.applyRepeat();
  },

  onTexture: function () {
    const mesh = this.el.getObject3D('mesh');
    if (!mesh || !mesh.material.map) return;
    this.texture = mesh.material.map;
    this.texture.wrapS = this.texture.wrapT = THREE.ClampToEdgeWrapping;
    this.applyRepeat();
  },

  applyRepeat: function () {
    this.texture.repeat.set(1 / this.data.columns, 1 / this.data.rows);
    this.showFrame(this.frame % this.data.frames);
  },

  showFrame: function (i) {
    const col = i % this.data.columns;
    const row = Math.floor(i / this.data.columns);
    this.texture.offset.set(col / this.data.columns, 1 - (row + 1) / this.data.rows);
    this.texture.needsUpdate = false;
  },

  tick: function (time, delta) {
    if (!this.texture || !this.data.playing) return;
    // Evita saltos tras volver de otra pestaña
    this.elapsed += Math.min(delta, 250);
    const step = 1000 / this.data.fps;
    while (this.elapsed >= step) {
      this.elapsed -= step;
      this.frame = (this.frame + 1) % this.data.frames;
      this.showFrame(this.frame);
    }
  },

  remove: function () {
    this.el.removeEventListener('materialtextureloaded', this.onTexture);
  }
});
