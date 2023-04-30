const slider = document.getElementById("clipSlider");
const value = document.getElementById("clipValue");


value.innerHTML = slider.value;



slider.oninput = function() {
  value.innerHTML = this.value;
}