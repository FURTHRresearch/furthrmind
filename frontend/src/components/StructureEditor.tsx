import {useEffect, useRef, useState} from "react";
import styles from './StructureEditor.module.css';

export default function ({
                             height = "100vh",
                             initialStructure = "",
                             onChange,
                         }) {
    const ketcher = useRef(null);
    const [ketcherFrame, setKetcherFrame] = useState(undefined)

    // const { current: id } = useRef(_uniqueId('ketcher-'));
    let id = "ketcher-"
    const handleLoad = () => {
        var currentKetcherFrame = document.getElementById(id);
        // @ts-ignore
        ketcher.current = currentKetcherFrame.contentWindow.ketcher;
        setKetcherFrame(ketcher.current)

        ketcher.current.editor.event.change.add(async () => {
            let smiles = await ketcher.current.getSmiles();
            let cdxml = await ketcher.current.getCDXml();

            // let smarts = await ketcher.current.getSmarts();
            // let molfile = await ketcher.current.getMolfile();

            onChange(smiles, cdxml);
        });
    }

    useEffect(() => {
        if (ketcherFrame) {
            ketcherFrame.setMolecule(initialStructure);
        }
    }, [ketcherFrame]);

    return (
        <div className="chemEditor" style={{height: height}}>
            <iframe className={styles.iframePlaceholder} onLoad={handleLoad} id={id}
                    src="/web/static/ketcher/index.html" width="100%" height="100%" title="Ketcher"></iframe>
        </div>
    );
};
