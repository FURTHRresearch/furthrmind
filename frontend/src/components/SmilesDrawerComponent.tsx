import React, {useRef, useEffect} from 'react';

import SmilesDrawer from 'smiles-drawer';
import Box from "@mui/material/Box";



const SmilesDrawerComponent = ({smiles}) => {


    const imgRef = useRef<HTMLImageElement>(null);
    const drawer = new SmilesDrawer.SmiDrawer(); // options is a param
    const [width, setWidth] = React.useState("100px")
    const [margin, setMargin] = React.useState("0px")
    useEffect(() => {
        drawer.draw(smiles, imgRef.current, 'light');
        if (smiles.includes(">>") || smiles.includes(".")) {
            setWidth("80%")
            setMargin("-70px")

        } else {
            setWidth("30%")
            setMargin("0px")
        }
    }, [smiles]);

    return (
        <Box marginTop={margin} marginBottom={margin} >
            <img ref={imgRef} width={width}
                 style={{display: "block", marginLeft: "auto", marginRight: "auto"}}></img>
        </Box>
    )
    // useEffect(() => {
    //     console.log(smiles)
    //     SmilesDrawer.parse(smiles, (tree) => {
    //         smilesDrawer.current.draw(tree, id);
    //     });
    // }, [smiles, id]);
    //
    // return (
    //     <div>
    //         <img id="imgExample" data-smiles-options="{ 'width': 400, 'height': 400 }"/>
    //
    //         <div>
    //             <svg id="svgExample"/>
    //         </div>
    //         <script type="text/javascript"
    //                 src="https://unpkg.com/smiles-drawer@2.0.1/dist/smiles-drawer.min.js"></script>
    //         <script>
    //             let moleculeOptions = {};
    //             let reactionOptions = {};
    //
    //             let sd = new SmiDrawer(moleculeOptions, reactionOptions);
    //             sd.draw('OC(C(=O)O[C@H]1C[N+]2(CCCOC3=CC=CC=C3)CCC1CC2)(C1=CC=CS1)C1=CC=CS1', '#imgExample')
    //             sd.draw('C=CCBr.[Na+].[I-]>CC(=O)C>C=CCI.[Na+].[Br-]', '#svgExample', 'dark')
    //         </script>
    //     </div>

    // <canvas id={id} width={height} height={height}></canvas>

}

export default SmilesDrawerComponent;