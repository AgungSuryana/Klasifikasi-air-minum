document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('prediction-form');
    const output = document.getElementById("prediction-results");
    const everydayOutput = document.getElementById("everyday-output"); // <- Tambahan
    const area = document.getElementById("results-area");
    const messageBox = document.getElementById("message-box");
    const messageText = document.getElementById("message-text");

    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = parseFloat(value);
        });

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Gagal memproses permintaan');

            const result = await response.json();

            area.classList.remove("hidden");

            if (result.prediction === 1) {
                output.innerHTML = `
                    <div class="flex flex-col items-center text-red-600">
                    <div class="text-[6rem] leading-none">✅</div>
                    <div class="text-2xl font-bold mt-2 text-center">Air Layak Minum</div>
                    </div>
                `;
                everydayOutput.innerHTML = ''; // kosongkan jika layak
            } else {
                let reasonList = '';

                if (Array.isArray(result.reasons) && result.reasons.length > 0) {
                    reasonList = `
                        <ul class="mt-4 list-disc list-inside text-md text-black text-left">
                            ${result.reasons.map(reason => `<li>${reason}</li>`).join('')}
                        </ul>
                    `;
                }

                output.innerHTML = `
                <div class="flex flex-col items-center text-red-600">
                <div class="text-[6rem] leading-none">❌</div>
                <div class="text-2xl font-bold mt-2 text-center">Air Tidak Layak Minum</div>
                </div>
                `;

                // Tambahkan ke everyday card
                everydayOutput.innerHTML = `
                    ${reasonList}
                `;
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
