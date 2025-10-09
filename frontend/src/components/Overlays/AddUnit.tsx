import { LoadingButton } from "@mui/lab";
import {
    Button, OutlinedInput, Stack, Typography
} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import axios from "axios";
import debounce from "lodash/debounce";
import React, { useMemo, useRef } from "react";
import ContentEditable from "react-contenteditable";
import { useParams } from "react-router-dom";
import useSWR from "swr";
import "./UnitEditor.css";
const fetcher = (url) => fetch(url).then((res) => res.json());

const AddUnit = (props) => {
    const { show, onClose } = props;
    return (
        <Dialog open={show} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle sx={{ padding: "10px 24px 5px 24px" }}>
                Edit custom unit
            </DialogTitle>
            <DialogContent>
                <Typography variant="body1" sx={{ color: "#6F7A7D", marginBottom: '1em' }}>
                    Define your own unit to fit your research.
                </Typography>
                <AddUnitCard {...props} />
            </DialogContent>
        </Dialog>
    );
};

const AddUnitCard = (props) => {
    const {
        initialName,
        initialDefinition,
        unitId,
        onClose
    } = props;

    const [definition, setDefinition] = React.useState(initialDefinition);
    const [name, setName] = React.useState(initialName);
    const [saving, setSaving] = React.useState(false);
    const [showUnitList, setShowUnitList] = React.useState(false);

    const params = useParams();

    const { data: units, mutate: mutateUnits } = useSWR(
        `/web/units?project=${"project" in params ? params.project : ""}`,
        fetcher
    );

    const error = useMemo(() => units.find((unit) => unit.name === name), [name, units]);

    const renderUnitDefinition = (definition: string) => {
        if (definition === null || definition === undefined) return "";
        let matches = definition.matchAll(/<u>(.*?)<\/u>/g);
        for (const m of matches) {
            definition = definition.replace(
                m[0],
                '<span class="unit" contentEditable="false" unit="' +
                m[1] +
                '">' +
                units.find((u) => u.id === m[1])?.Name +
                "</span>"
            );
        }
        return definition;
    };

    const validateDefinition = useRef(debounce((definition, units) => {
        let us = [...units].sort((a, b) => b.Name.length - a.Name.length);
        definition = definition.replaceAll('&nbsp;', '')
        for (const u of us) {
            if (u.id != unitId && u.Name.length > 0 && definition.includes(u.Name)) {
                definition = definition.replaceAll(u.Name, "<u>" + u.id + "</u>")
            }
        }
        setDefinition(definition);
    }, 500)).current;

    const parseUnitDefinition = (definition) => {
        let matches = definition.matchAll(/<span .*? unit="(.*?)".*?>.*?<\/span>/g);
        for (const m of matches)
            definition = definition.replace(m[0], "<u>" + m[1] + "</u>");
        setDefinition(definition);
        validateDefinition(definition, units);
    };

    const handleSave = () => {
        let def = definition.replaceAll('&nbsp;', '');
        if (unitId.length > 0) {
            axios.post('/web/units/' + unitId, { definition: def, name })
            mutateUnits(units.map((unit) => unit.id === unitId ? { ...unit, Definition: def, Name: name } : unit), false);
            onClose();
        } else {
            setSaving(true);
            axios.post(`/web/projects/${params.project}/units`, {
                name, definition: def
            }).then(r => {
                mutateUnits(units.concat({ id: r.data.id, Name: name, Definition: definition, editable: true }), false);
                onClose();
            }).catch(err => {
                alert('Unit name already exists.');
                onClose();
            });;
        }
    }

    return (
        <Grid container spacing={2}>
            {/* <Grid item md={12} xs={12} >
                <Stack mt={3}>
                    <Typography variant="subtitle2" sx={{ color: "#6F7A7D" }} mb={1}>
                        Unit category
                    </Typography>
                    <CustomAutoComplete
                        list={categoryList}
                        type="category"
                        addNewData={addNewData}
                        initValue={data.category.title ?? ''}
                        label="category"
                        refresh={refresh}
                        editData={editData}
                        editMode={editID !== ''}
                    />
                </Stack>
            </Grid> */}
            <Grid item md={12} xs={12}>
                <Stack>
                    <Typography variant="subtitle2" sx={{ color: "#6F7A7D" }} mb={1}>
                        Unit Name
                    </Typography>
                    <OutlinedInput
                        notched={false}
                        placeholder="Enter unit name"
                        label="Unit name"
                        onChange={(e) => setName(e.target.value)}
                        value={name}
                        size="medium"
                        fullWidth
                        error={error}
                    />
                    {error && <Typography variant='subtitle1' sx={{ color: 'red' }}>
                        Name is already defined.
                    </Typography>}
                </Stack>
            </Grid>
            <Grid item md={12} xs={12}>
                <Stack>
                    <Typography variant="subtitle2" sx={{ color: "#6F7A7D" }} mb={1}>
                        Unit definition
                    </Typography>
                    {/* <AutoGenerateField
                        type='definition'
                        definitionList={definitionList}
                        refresh={refresh}
                        addNewData={addNewData}
                        initValue={data.definition.title ?? ''}
                        editData={editData}
                        editMode={editID !== ''}
                    /> */}
                    <ContentEditable
                        style={{ width: '100%', borderBottom: "1px solid #e0e0e0", textDecoration: "none" }}
                        html={renderUnitDefinition(definition)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") e.preventDefault();
                        }}
                        onChange={(e: any) => parseUnitDefinition(e.target.value)}
                    />
                </Stack>
            </Grid>
            <div style={{ width: '100%', textAlign: 'right' }}>
                <span style={{ textDecoration: 'underline', cursor: 'pointer' }} onClick={() => setShowUnitList(true)}>Use any of these predefined units</span>
                <UnitListOverlay show={showUnitList} onClose={() => setShowUnitList(false)} />
            </div>
            <Grid item md={5} display='flex'>
                <Grid item md={6}>
                    <Stack direction="row" spacing={2}>
                        <LoadingButton loading={saving} variant="contained" onClick={handleSave}>
                            Save
                        </LoadingButton>
                        <Button variant='outlined' onClick={onClose}>
                            Cancel
                        </Button>
                    </Stack>
                </Grid>
            </Grid>
        </Grid>
    )
}

export default AddUnit;

function groupBy(xs, key) {
    return xs.reduce(function (rv, x) {
        (rv[x[key]] = rv[x[key]] || []).push(x);
        return rv;
    }, {});
};

function UnitListOverlay({ show, onClose }) {

    const params = useParams();

    const { data: units } = useSWR(
        `/web/units?project=${"project" in params ? params.project : ""}`,
        fetcher
    );

    const groups = useMemo(() => groupBy(units, 'category'), [units])

    return (<Dialog open={show} onClose={onClose} fullWidth maxWidth="md">
        <DialogTitle sx={{ padding: "10px 24px 5px 24px" }}>
            Defined Units
        </DialogTitle>
        <DialogContent>
            <Typography variant="body1" sx={{ color: "#6F7A7D", marginBottom: '1em' }}>
                Use these units in custom definitions.
            </Typography>
            <div>
                {Object.keys(groups).map((category) => <>
                    <Typography variant="h6" sx={{ color: "#6F7A7D" }}>
                        {category}
                    </Typography>
                    <Typography variant="body1" style={{ marginBottom: '1em' }}>
                        {groups[category].map((unit) =>
                            <> {unit.Name}, </>)}
                    </Typography>

                </>)}
            </div>
        </DialogContent>
    </Dialog>)

}