import {Backdrop} from '@mui/material';
import {useEffect, useState} from 'react';
import './LightBox.css';
import "tiff.js/tiff.min"

const LightBox = ({show, onClose, images, initialIndex}) => {
    const [index, setIndex] = useState(initialIndex);

    const updateIndex = (index: number, e) => {
        e.stopPropagation();
        if (index < 0) index = images.length - 1;
        if (index >= images.length) index = 0;
        setIndex(index);
    }
    const handleKeyDown = (event) => {
        const {keyCode} = event;
        if (keyCode === 27) {
            onClose();
        }

    };

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);

        // cleanup this component
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    useEffect(() => {
        let fileName = images[index].Name
        let fileExt = fileName.split('.').pop()
        if (["tiff", "tif"].includes(fileExt)) {
            var xhr = new XMLHttpRequest()
            xhr.responseType = "arraybuffer"
            xhr.open("GET", "/web/files/" + images[index].id)

            xhr.onload = function (e) {
                var arrayBuffer = xhr.response
                Tiff.initialize({
                    TOTAL_MEMORY: 16777216 * 10
                })
                var tiff = new Tiff({
                    buffer: arrayBuffer
                })
                var dataUri = tiff.toDataURL()
                document.getElementById("img").src = dataUri
            }
            xhr.send()
        } else {
            let dataUri = "/web/files/" + images[index].id
            let doc = document.getElementById("img")
            doc.src = dataUri
        }
    }, [index]);

    return (
        <Backdrop

            open={show} onClick={onClose}
            sx={{color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#000'}}>
            <div className="lb-modal-content">

                <div className="lb-slides">
                    <img className="graph" id="img" alt=""/>
                </div>

                <span className="lb-prev" onClick={(e) => updateIndex(index - 1, e)}>&#10094;</span>
                <span className="lb-next" onClick={(e) => updateIndex(index + 1, e)}>&#10095;</span>

                <div className="lb-caption-container">
                    <p id="lb-caption"></p>
                </div>

                <div className="lb-thumbs">
                    {images.map((img, i) =>
                        <img
                            key={img.id}
                            className={"graph lb-db " + ((i === index) ? "lb-active" : "")}
                            src={"/web/files/" + img.Thumbnail} onClick={(e) => updateIndex(i, e)}
                            alt=""/>)}
                </div>

            </div>
        </Backdrop>
    );
}

export default LightBox;