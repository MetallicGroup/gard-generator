# Gard AI – Generator imagine AI cu Render & ImgBB

Acest microserver primește o imagine + model de gard, simulează modificarea gardului, și returnează un link public al imaginii noi folosind ImgBB.

## Endpoint
`POST /process`

Payload:
```json
{
  "image_url": "https://...",
  "model": "MX25"
}
