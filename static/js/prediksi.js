document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('prediction-form');
    const output = document.getElementById("prediction-results");
    const everydayOutput = document.getElementById("everyday-output");
    const area = document.getElementById("results-area");
    const messageBox = document.getElementById("message-box");
    const messageText = document.getElementById("message-text");

    // Pastikan form ada
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault(); // Cegah reload halaman

        const formData = new FormData(form);
        const data = {};

        // Konversi FormData ke format JSON
        formData.forEach((value, key) => {
            data[key] = parseFloat(value); // pastikan nilai jadi number
        });

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Gagal memproses permintaan');

            const result = await response.json();

            // Tampilkan card hasil prediksi
            area.classList.remove("hidden");

            if (result.prediction === 1) {
                output.innerHTML = `
                    <div class="flex flex-col items-center text-green-600">
                        <div class="text-[6rem] leading-none">✅</div>
                        <div class="text-2xl font-bold mt-2 text-center">Air Layak Minum</div>
                    </div>
                `;
                everydayOutput.innerHTML = ''; // kosongkan alasan
            } else {
                let reasonList = '';
                let suggestionList = '';

                if (Array.isArray(result.reasons) && result.reasons.length > 0) {
                    reasonList = `
                        <div class="mt-4">
                            <h3 class="text-md font-semibold text-red-700 mb-2">Alasan tidak layak:</h3>
                            <ul class="list-disc list-inside text-sm text-black">
                                ${result.reasons.map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (Array.isArray(result.suggestions) && result.suggestions.length > 0) {
                    suggestionList = `
                        <div class="mt-4">
                            <h3 class="text-md font-semibold text-blue-700 mb-2">Saran perbaikan:</h3>
                            <ul class="list-disc list-inside text-sm text-black">
                                ${result.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                output.innerHTML = `
                    <div class="flex flex-col items-center text-red-600">
                        <div class="text-[6rem] leading-none">❌</div>
                        <div class="text-2xl font-bold mt-2 text-center">Air Tidak Layak Minum</div>
                    </div>
                `;

                everydayOutput.innerHTML = reasonList + suggestionList;
            }

        } catch (error) {
            console.error("Error saat prediksi:", error);
            if (messageBox && messageText) {
                messageBox.classList.remove("hidden");
                messageText.innerText = "Terjadi kesalahan saat mengirim data. Silakan coba lagi.";
            }
        }
    });
});
