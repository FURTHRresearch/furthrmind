import CheckboxField from './CheckboxField';
import ChemicalStructureField from './ChemicalStructureField';
import ComboboxField from './ComboboxField';
import DataCalcField from './DataCalcField';
import DateField from './DateField';
import FileField from './FileField';
import NotebookField from './NotebookField';
import NumericField from './NumericField';
import NumericRangeField from "./NumericRangeField";
import SinglelineField from './SinglelineField';

const AutoField = ({
                       controlled = false,
                       data,
                       readOnly = false,
                       parentId = null,
                       onChange = (val) => null,
                       onUnitChange = (val) => null,
                       parentType = null,
                       writable = true,
                       admin = false,
                       menuDisabled = false,
                       validator = (val) => true
                   }) => {
    const value = controlled ? data.Value : null;
    const unitId = controlled ? data.UnitID : null;
    const generalProps = {
        key: data.id,
        parentId,
        parentType,
        writable,
        admin,
        authorId: data.AuthorID,
        label: data.Name,
        fieldDataId: data.id,
        fieldId: data.FieldID,
        onChange,
        onUnitChange,
        value,
        unitId,
        menuDisabled,
        validator
    }

    if (data.Type === "ChemicalStructure")
        return <ChemicalStructureField initialSmiles={data.smiles} {...generalProps} value={data.Value}/>


    if (data.Type === "File")
        return <FileField initialValue={data.Value} {...generalProps} />;

    if (data['Type'] === 'Numeric')
        return (
            <NumericField
                initialValue={data["Value"]}
                initialUnitId={data["UnitID"] ? data["UnitID"] : '-'}
                {...generalProps}
            />
        )

    if (data['Type'] === 'NumericRange')
        return (
            <NumericRangeField
                initialValue={data["Value"]}
                initialUnitId={data["UnitID"] ? data["UnitID"] : '-'}
                {...generalProps}
            />
        )

    if (data['Type'] === 'SingleLine') {
        return (
            <SinglelineField
                initialValue={data["Value"]}
                {...generalProps}
            />
        )
    }

    if (data['Type'] === 'CheckBox')
        return (
            <CheckboxField
                initialValue={data["Value"]}
                {...generalProps}
                onChange={onChange}
            />
        )

    if (data['Type'] === 'MultiLine')
        return (
            <NotebookField
                notebookId={data["Value"]}
                {...generalProps}
                initialTeaser={data["Teaser"]}
            />
        )

    if (data['Type'] === 'Date') {
        return (
            <DateField
                initialValue={data["Value"]}
                {...generalProps}
            />
        )
    }

    if (data['Type'] === 'RawDataCalc')
        return (
            <DataCalcField
                {...generalProps}
                data={data}/>
        )

    if (data['Type'] === 'ComboBox' || data['Type'] === "ComboBoxSynonym")
        return (
            <ComboboxField
                initialValue={data["Value"]}
                fieldId={data["FieldID"]}
                dataId={data["id"]}
                onChange={onChange}
                admin={admin}
                {...generalProps} />
        )

    return (
        <p> Field not supported </p>
    )
}

export default AutoField;
