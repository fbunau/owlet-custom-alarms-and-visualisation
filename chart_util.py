import altair as alt


def build_dual_axis_altair_time_chart(
    data, title, time_interval, time_unit, time_field, 
    field1, field1_tooltip, field1_domain, field1_color,
    field2, field2_tooltip, field2_domain, field2_color
):
  hover = alt.selection_single(
    fields=[time_field],
    nearest=True,
    on="mouseover",
    empty="none",
  )

  o2_line = (
    alt.Chart(data, title=f"{title} ({time_interval} {time_unit})")
      .mark_line()
      .encode(
        alt.Y(f"{field1}:Q", scale=alt.Scale(domain=field1_domain)),
        alt.X(time_field, axis=alt.Axis(tickSize=0)),
        color=alt.value(field1_color)
      )
  )

  bpm_line = (
    alt.Chart(data)
      .mark_line()
      .encode(
        alt.Y(f"{field2}:Q", scale=alt.Scale(domain=field2_domain)),
        alt.X(time_field, axis=alt.Axis(tickSize=0)),
        color=alt.value(field2_color)
      )
  )

  # Draw points on the line, and highlight based on selection
  points = o2_line.transform_filter(hover).mark_circle(size=65)

  # Draw a rule at the location of the selection
  tooltips = (
    alt.Chart(data)
      .mark_rule()
      .encode(
        x="time",
        y="o2",
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[
          alt.Tooltip("time", title="Time"),
          alt.Tooltip("o2", title=field1_tooltip),
          alt.Tooltip("bpm", title=field2_tooltip),
        ],
      )
      .add_selection(hover)
  )

  line_layer = alt.layer(o2_line, bpm_line).resolve_scale(
    y = 'independent'
  )

  return (line_layer + points + tooltips).interactive().configure_axisX(ticks=False, labels=False)