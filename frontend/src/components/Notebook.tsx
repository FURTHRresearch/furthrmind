import React, { useCallback } from 'react';

import '@toast-ui/editor/dist/theme/toastui-editor-dark.css';
import '@toast-ui/editor/dist/toastui-editor.css';

import { Editor } from '@toast-ui/react-editor';
import useSWR from 'swr';

import debounce from 'lodash/debounce';

const Notebook = ({ notebookId, height = '90vh', onChange = (v) => null }) => {
    const editorRef = React.useRef(null);
    const { data, mutate } = useSWR(`/web/notebooks/${notebookId}/content`,
        (url: string) => fetch(url).then(r => r.json()))

    // eslint-disable-next-line
    const saveEditor = useCallback(debounce(() => {
        let content = editorRef.current.getInstance().getMarkdown()
        onChange(content);
        fetch('/web/notebooks/' + notebookId, {
            method: 'POST',
            // @ts-ignore
            body: content
        });
        mutate({...data, content: content}, false)
    }, 500), [notebookId, onChange]);
    const addImage = (blob, callback) => {
        fetch('/nbfiles/upload', {
            method: 'POST',
            body: blob
        }).then(function (response) {
            response.text().then(function (text) {
                callback('/nbfiles/' + text, '');
            });
        });
        return false;
    }

    return data === undefined ? <>Loading...</> :
        <Editor
            initialEditType="wysiwyg"
            // @ts-ignore
            initialValue={data.content}
            height={height}
            ref={editorRef}
            onChange={saveEditor}
            hooks={{
                addImageBlobHook: addImage
            }
            }
            theme={window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : ''}
        />

}

export default Notebook;
