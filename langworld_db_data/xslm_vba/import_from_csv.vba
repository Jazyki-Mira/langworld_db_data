Const constSeparator As String = "&"

Sub ImportRemoteCSVAndInsert()

    Call SecImportCSV
    Call SecCopyImportedColumnsToInputSheet
    Call SplitMultiSelectFeatures

End Sub
Sub SecImportCSV()

    Dim strLanguage As String

    strLanguage = Replace(ThisWorkbook.Name, ".xlsm", "")

    ActiveWorkbook.Queries.Add Name:=strLanguage, Formula:= _
        "let" & Chr(13) & "" & Chr(10) & "    Источник = Csv.Document(Web.Contents(""https://raw.githubusercontent.com/lemontree210/langworld_db_data/master/data/feature_profiles/" & strLanguage & ".csv""),[Delimiter="","", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None])," & Chr(13) & "" & Chr(10) & "    #""Повышенные заголовки"" = Table.PromoteHeaders(Источник, [PromoteAllScalars=true])," & Chr(13) & "" & Chr(10) & "    #""Измененный тип"" = Table.TransformColumnTypes(#""Повышенные заголовки"",{{""feature_id"", type text}, {""" & _
        "feature_name_ru"", type text}, {""value_type"", type text}, {""value_id"", type text}, {""value_ru"", type text}, {""comment_ru"", type text}, {""comment_en"", type text}, {""page_numbers"", Int64.Type}})," & Chr(13) & "" & Chr(10) & "    #""Добавлен пользовательский объект"" = Table.AddColumn(#""Измененный тип"", ""value_id_and_value"", each if [value_type] = ""listed"" then [value_id] & "": "" & [value_ru] else """")," & Chr(13) & "" & Chr(10) & "   " & _
        " #""Переупорядоченные столбцы"" = Table.ReorderColumns(#""Добавлен пользовательский объект"",{""feature_id"", ""feature_name_ru"", ""value_type"", ""value_id"", ""value_ru"", ""value_id_and_value"", ""comment_ru"", ""comment_en"", ""page_numbers""})," & Chr(13) & "" & Chr(10) & "    #""Условный столбец добавлен"" = Table.AddColumn(#""Переупорядоченные столбцы"", ""value_custom"", each if [value_type] = ""custom" & _
        """ then [value_ru] else """")," & Chr(13) & "" & Chr(10) & "    #""Переупорядоченные столбцы1"" = Table.ReorderColumns(#""Условный столбец добавлен"",{""feature_id"", ""feature_name_ru"", ""value_type"", ""value_id"", ""value_ru"", ""value_id_and_value"", ""value_custom"", ""comment_ru"", ""comment_en"", ""page_numbers""})," & Chr(13) & "" & Chr(10) & "    #""Удаленные столбцы"" = Table.RemoveColumns(#""Переупорядоченные столбцы1"",{""val" & _
        "ue_ru""})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Удаленные столбцы"""
    ActiveWorkbook.Worksheets.Add
    With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
        "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=" & strLanguage & ";Extended Properties=""""" _
        , Destination:=Range("$A$1")).QueryTable
        .CommandType = xlCmdSql
        .CommandText = Array("SELECT * FROM [" & strLanguage & "]")
        .RowNumbers = False
        .FillAdjacentFormulas = False
        .PreserveFormatting = True
        .RefreshOnFileOpen = False
        .BackgroundQuery = True
        .RefreshStyle = xlInsertDeleteCells
        .SavePassword = False
        .SaveData = True
        .AdjustColumnWidth = True
        .RefreshPeriod = 0
        .PreserveColumnInfo = True
        .ListObject.DisplayName = strLanguage
        .Refresh BackgroundQuery:=False
    End With
End Sub


Sub SecCopyImportedColumnsToInputSheet()
'
' CopyImportedColumnsToInputSheet Макрос
'
    Dim strLanguage As String

    strLanguage = Replace(ThisWorkbook.Name, ".xlsm", "")

    Sheets("input").Unprotect

    Sheets("Лист1").Select
    Range(strLanguage & "[feature_id]").Select
    Selection.Copy
    ActiveSheet.Next.Select
    Range("A2").Select
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    ActiveSheet.Previous.Select
    Range(strLanguage & "[value_type]").Select
    Application.CutCopyMode = False
    Selection.Copy
    ActiveSheet.Next.Select
    Range("C2").Select
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    ActiveSheet.Previous.Select
    Range(strLanguage & "[[value_id_and_value]:[comment_ru]]").Select
    Application.CutCopyMode = False
    Selection.Copy
    ActiveSheet.Next.Select
    Range("E2").Select
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False

    'add page numbers
    ActiveSheet.Previous.Select
    Range(strLanguage & "[page_numbers]").Select
    Application.CutCopyMode = False
    Selection.Copy
    ActiveSheet.Next.Select
    Range("I2").Select
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=False

    Range("A2").Select

    Sheets("input").Protect DrawingObjects:=True, Contents:=True, Scenarios:=True _
        , AllowFormattingColumns:=True, AllowFiltering:=True

    Sheets("Лист1").Select
    ActiveWindow.SelectedSheets.Visible = False

End Sub


Sub SplitMultiSelectFeatures()
'
' Split lines with compound values like "I-1&I-2: Past&Present"
' into separate lines with one elementary value per line
'
    Dim strValueId As String
    Dim strValueName As String
    Dim strFeatureId As String
    Dim strFeatureName As String
    Dim strValueType As String

    Dim intElementaryValueCount As Integer
    Dim i As Integer

    Dim arrValueIDs
    Dim arrValueNames

    Dim rngFoundCell

    Sheets("input").Unprotect

    Range("InputForm[ValueID]").Select
    Set rngFoundCell = Selection.Find(What:=constSeparator, After:=ActiveCell, LookIn:=xlValues, LookAt:= _
        xlPart, SearchOrder:=xlByRows, SearchDirection:=xlNext, MatchCase:=False _
        , SearchFormat:=False)

    If rngFoundCell Is Nothing Then
        Cells(1, 1).Select
        Debug.Print "No (more) compound values found"
        Exit Sub
    End If

    rngFoundCell.Select

    strValueId = Selection.Value

    strFeatureId = ActiveCell.Offset(0, -3).Value
    strValueType = ActiveCell.Offset(0, -1).Value
    'Feature name is set using a formula, so not setting here

    ' Option Base 1 will not affect the result of Split, it will be from 0 anyway. So I don't declare Option Base 1 in this module
    strValueName = ActiveCell.Offset(0, 1).Value
    Debug.Print "Splitting compound value " & strValueName
    strValueName = Split(strValueName, ": ")(1)

    arrValueIDs = Split(strValueId, constSeparator)
    arrValueNames = Split(strValueName, constSeparator)

    intElementaryValueCount = UBound(arrValueIDs)

    For i = 1 To intElementaryValueCount
        Selection.ListObject.ListRows.Add (Selection.Row)
    Next i

    For i = 0 To intElementaryValueCount
        ActiveCell.Offset(i, 0).Value = arrValueIDs(i)
        ActiveCell.Offset(i, 1).Value = arrValueIDs(i) & ": " & arrValueNames(i)
        ActiveCell.Offset(i, -3).Value = strFeatureId
        ActiveCell.Offset(i, -1).Value = strValueType
    Next i

    ' repeat with next compound value
    Call SplitMultiSelectFeatures

    Sheets("input").Protect

End Sub
