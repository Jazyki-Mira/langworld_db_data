Option Explicit
Const cStartMarker As String = "&#"
Const cEndMarker As String = ";"


Private Sub Worksheet_Change(ByVal Target As Range)

    Const cListedValueColumn As Byte = 5
    Const cCustomValueColumn As Byte = 6
    Const cCommentColumn As Byte = 7
    Const cEnglishCommentColumn As Byte = 8

    ' Exit Sub when working with range cells: here I only work with single cells
    If Target.Cells.Count > 1 Then Exit Sub

    'Potential character conversion

    'Exit if it is a single cell but it is empty
    If Len(Target.Value) = 0 Then Exit Sub

    If InStr(1, Target.Value, cStartMarker) = 0 Then Exit Sub

    If Target.Column = cCommentColumn Or Target.Column = cCustomValueColumn Or Target.Column = cEnglishCommentColumn Then

        Call ConvertToUnicode(Target)

    End If

End Sub


Sub ConvertToUnicode(rngX As Range)

    Dim strX As String

    Dim lngStart As Long
    Dim lngEnd As Long

    Dim strCharCodeExpression As String
    Dim strCharCode As String
    Dim lngCharCode As Long

    strX = rngX.Value

    Do
        lngStart = InStr(1, strX, cStartMarker)
        If lngStart = 0 Then Exit Do

        lngEnd = InStr(lngStart, strX, cEndMarker)
        If lngEnd > 0 Then
            strCharCodeExpression = Mid(strX, lngStart, lngEnd - lngStart + Len(cEndMarker))

            ' Delete markers
            strCharCode = Replace(strCharCodeExpression, cStartMarker, "")
            strCharCode = Replace(strCharCode, cEndMarker, "")

            On Error GoTo StringToNumberConversionError
            lngCharCode = CLng(strCharCode)

            On Error GoTo UnicodeConversionError
            strX = Replace(strX, strCharCodeExpression, ChrW(lngCharCode))

            On Error GoTo 0

        End If

    Loop

    rngX.Value = strX

    Exit Sub

StringToNumberConversionError:
    MsgBox ("Ошибка конвертации символа " & strCharCodeExpression & ": код " & strCharCode & " не является целым числом")
    Exit Sub

UnicodeConversionError:
    MsgBox ("Ошибка конвертации символа " & strCharCodeExpression)

End Sub
