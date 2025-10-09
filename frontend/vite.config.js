import react from "@vitejs/plugin-react";
import {defineConfig} from "vite";


export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '^(\/web)|(\/dev$)|^(\/logout)|^(\/files)|^(\/onlyoffice)|^(\/dataviews)|^(\/dataviewcharts)|^(\/s3)|^(\/tus-upload)|^(\/confirm-new-email)|^(\/units)|^(\/fields)|^(\/webdatacalc)|^(\/comboboxes)|^(\/comboboxentries)|^(\/groups)|^(\/notebooks)|^(\/nbfiles)|^(\/rawdata)|^(\/columns)|^(\/permissions)|^(\/api2)|^(\/login_demo)|^(\/filter)|^(\/test-glitchtip)': {
                target: 'http://127.0.0.1:5000',
                changeOrigin: true,
                hostRewrite: 'localhost:3000'
            }
        }
    },
    esbuild: {
        minifyIdentifiers: false
    },
    build: {
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (id.includes('node_modules')) {
                        return id.toString().split('node_modules/')[1].split('/')[0].toString();
                    }
                }
            }
        }
    },

});