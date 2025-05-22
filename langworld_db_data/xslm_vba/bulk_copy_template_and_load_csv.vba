Sub ProcessNames()
    ' this macro was created with AI assistance

    Dim namesList As Variant
    Dim nameItem As Variant
    Dim templatePath As String
    Dim newFilePath As String
    Dim wb As Workbook
    Dim app As Application

    ' Insert doculect IDs:
    namesList = Array( _
        "abaza", "adyghe" _
    )

    ' Set your folder path (no trailing backslash)
    templatePath = "C:\...\_template.xlsm" ' <-- Edit as needed

    Set app = Application

    For Each nameItem In namesList
        ' Build new file path
        newFilePath = "C:\...\output\" & nameItem & ".xlsm" ' <-- Edit path to directory

        ' Open template
        Set wb = app.Workbooks.Open(templatePath)

        ' Save as new file
        wb.SaveAs Filename:=newFilePath, FileFormat:=xlOpenXMLWorkbookMacroEnabled

        ' Run the macro to load from remote CSV in the new workbook
        ' Comment this line if there is no remote CSV for this doculect
        app.Run "'" & wb.Name & "'!ImportRemoteCSVAndInsert"

        ' Save and close
        wb.Save
        wb.Close SaveChanges:=False
    Next nameItem
End Sub
