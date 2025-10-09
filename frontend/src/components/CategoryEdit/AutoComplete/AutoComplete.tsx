import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete, { createFilterOptions } from "@mui/material/Autocomplete";

const filter = createFilterOptions();

export default function FreeSoloCreateOption(props) {
  const { list, addNewData, type, label, refresh, editMode, editData } = props;
  const [value, setValue] = useState(null);

  const addNewDataHandler = (value, isNew) => {
    addNewData(value, type, isNew);
  };

  const performCleanUp = () => {
    setValue(null);
  };

  useEffect(() => {
    performCleanUp();
  }, [refresh]);

  useEffect(() => {
    if (editMode && Object.keys(editData).length > 0) {
      if (editData[type] && editData[type].title) {
        const val = editData[type].title || "";
        setValue(val);
      }
    }
  }, [editMode, editData])


  return (
    <Autocomplete
      value={value}
      onChange={(event, newValue) => {
        if (typeof newValue === "string") {
          addNewDataHandler(newValue, false);
          setValue({
            title: newValue,
          });
        } else if (newValue && newValue.inputValue) {
          // Create a new value from the user input
          addNewDataHandler({ title: newValue.inputValue }, true);
          setValue({
            title: newValue.inputValue,
          });
        } else {
          addNewDataHandler(newValue, false);
          setValue(newValue);
        }
      }}
      filterOptions={(options, params) => {
        const filtered = filter(options, params);

        const { inputValue } = params;
        // Suggest the creation of a new value
        const isExisting = options.some(
          (option) => inputValue === option.title
        );
        if (inputValue !== "" && !isExisting) {
          filtered.push({
            inputValue,
            title: `Add "${inputValue}"`,
          });
        }

        return filtered;
      }}
      selectOnFocus
      clearOnBlur
      handleHomeEndKeys
      id="free-solo-with-text-demo"
      options={list}
      getOptionLabel={(option) => {
        // Value selected with enter, right from the input
        if (typeof option === "string") {
          return option;
        }
        // Add "xxx" option created dynamically
        if (option.inputValue) {
          return option.inputValue;
        }
        // Regular option
        return option.title;
      }}
      renderOption={(props, option) => <li {...props}>{option.title}</li>}
      freeSolo
      renderInput={(params) => (
        <TextField {...params} label={`Search ${label}`} />
      )}
    />
  );
}
