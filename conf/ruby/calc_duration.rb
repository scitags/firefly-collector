require 'time'

def filter(event)
  begin
    start_time = Time.parse(event.get('[flow-lifecycle][start-time]')).to_f
    end_time = Time.parse(event.get('[flow-lifecycle][end-time]')).to_f
    if end_time >= start_time then
      event.set('[flow-lifecycle][duration]', (end_time - start_time).round(3))
      return [event]
    end
  rescue => exception
    logger.debug('Error parsing start and end time')
    return [event]
  end
end
