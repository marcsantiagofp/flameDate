const configIcon = document.getElementById("toggleConfig");
const configPanel = document.getElementById("config-panel");
const flameList = document.getElementById("flameList");
const distanceRange = document.getElementById("distanceRange");
const distanceValue = document.getElementById("distanceValue");
const minAgeSlider = document.getElementById("minAge");
const maxAgeSlider = document.getElementById("maxAge");
const ageValue = document.getElementById("ageValue");

let configVisible = false;

configIcon?.addEventListener("click", () => {
  configVisible = !configVisible;
  configPanel?.classList.toggle("d-none", !configVisible);
  flameList?.classList.toggle("d-none", configVisible);

  const tabs = document.querySelector(".tabs");
  const configTitle = document.querySelector(".config-title");

  if (configVisible) {
    tabs?.classList.add("d-none");
    configTitle?.classList.remove("d-none");
  } else {
    tabs?.classList.remove("d-none");
    configTitle?.classList.add("d-none");
  }
});

function updateSingleSliderBackground(input) {
  const val = parseInt(input.value);
  const min = parseInt(input.min);
  const max = parseInt(input.max);
  const percent = ((val - min) / (max - min)) * 100;
  input.style.background = `linear-gradient(to right, #ff4d4d 0%, #ff4d4d ${percent}%, rgba(255,255,255,0.2) ${percent}%)`;
}

function updateDualSliderBackground() {
  const min = parseInt(minAgeSlider.min);
  const max = parseInt(maxAgeSlider.max);
  const minVal = parseInt(minAgeSlider.value);
  const maxVal = parseInt(maxAgeSlider.value);

  const minPercent = ((minVal - min) / (max - min)) * 100;
  const maxPercent = ((maxVal - min) / (max - min)) * 100;

  const gradient = 
    `linear-gradient(to right,
      rgba(255,255,255,0.2) ${minPercent}%,
      #ff4d4d ${minPercent}%,
      #ff4d4d ${maxPercent}%,
      rgba(255,255,255,0.2) ${maxPercent}%)`;

  minAgeSlider.style.background = gradient;
  maxAgeSlider.style.background = gradient;
}

function updateDualSlider() {
  const minVal = parseInt(minAgeSlider.value);
  const maxVal = parseInt(maxAgeSlider.value);

  ageValue.textContent = `${minVal} - ${maxVal}`;
  updateDualSliderBackground();
}

distanceRange?.addEventListener("input", () => {
  distanceValue.textContent = `${distanceRange.value} km`;
  updateSingleSliderBackground(distanceRange);
});

minAgeSlider.addEventListener("input", () => {
  let minVal = parseInt(minAgeSlider.value);
  let maxVal = parseInt(maxAgeSlider.value);

  // Si el mínimo supera el máximo, mueve el máximo
  if (minVal > maxVal - 1) {
    maxVal = minVal + 1;
    if (maxVal > parseInt(maxAgeSlider.max)) {
      maxVal = parseInt(maxAgeSlider.max);
      minVal = maxVal - 1;
      minAgeSlider.value = minVal;
    }
    maxAgeSlider.value = maxVal;
  }

  updateDualSlider();
});

maxAgeSlider.addEventListener("input", () => {
  let minVal = parseInt(minAgeSlider.value);
  let maxVal = parseInt(maxAgeSlider.value);

  // Si el máximo es menor o igual al mínimo, mueve el mínimo
  if (maxVal < minVal + 1) {
    minVal = maxVal - 1;
    if (minVal < parseInt(minAgeSlider.min)) {
      minVal = parseInt(minAgeSlider.min);
      maxVal = minVal + 1;
      maxAgeSlider.value = maxVal;
    }
    minAgeSlider.value = minVal;
  }

  updateDualSlider();
});

window.addEventListener("DOMContentLoaded", () => {
  if (distanceRange) {
    distanceValue.textContent = `${distanceRange.value} km`;
    updateSingleSliderBackground(distanceRange);
  }
  if (minAgeSlider && maxAgeSlider) {
    updateDualSlider();
  }
});
